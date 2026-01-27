FROM python:3.14-alpine AS builder

ENV PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies for Python wheels and gunicorn modules
RUN apk add --no-cache \
    build-base \
    cargo \
    curl \
    freetype-dev \
    git \
    lcms2-dev \
    libffi-dev \
    libjpeg-turbo-dev \
    linux-headers \
    openjpeg-dev \
    openssl-dev \
    pkgconf \
    postgresql-dev \
    rust \
    tiff-dev \
    zlib-dev

WORKDIR /tmp/build
COPY requirements.txt ./

# Install Python dependencies (including gunicorn + gevent) into a relocatable prefix
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install --no-compile --root /install -r requirements.txt gunicorn gevent

FROM python:3.14-alpine

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production

# Runtime dependencies only
RUN apk add --no-cache \
    ca-certificates \
    freetype \
    git \
    curl \
    lcms2 \
    libffi \
    libjpeg-turbo \
    libstdc++ \
    openjpeg \
    openssl \
    postgresql-libs \
    tini \
    tiff \
    zlib

ARG FRONTEND_WORKERS=4
ARG FRONTEND_THREADS=2
ARG GUNICORN_WORKER_CLASS="gevent"
ARG GUNICORN_BIND="0.0.0.0:80"
ARG GUNICORN_MAX_REQUESTS=150000
ARG GUNICORN_MAX_REQUESTS_JITTER=1000
ARG GUNICORN_TIMEOUT=45

ENV FRONTEND_WORKERS=${FRONTEND_WORKERS} \
    FRONTEND_THREADS=${FRONTEND_THREADS} \
    GUNICORN_WORKER_CLASS=${GUNICORN_WORKER_CLASS} \
    GUNICORN_BIND=${GUNICORN_BIND} \
    GUNICORN_MAX_REQUESTS=${GUNICORN_MAX_REQUESTS} \
    GUNICORN_MAX_REQUESTS_JITTER=${GUNICORN_MAX_REQUESTS_JITTER} \
    GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT}

WORKDIR /stern

# Copy only the installed packages from the builder layer
COPY --from=builder /install/usr/local /usr/local

# Copy application source
COPY . .

# Precompile python files for faster startup
RUN python -m compileall -q app

# Setup volume for app/static
VOLUME /stern/app/static

STOPSIGNAL SIGQUIT
ENTRYPOINT ["/sbin/tini", "--"]

CMD ["sh", "-c", "gunicorn --bind ${GUNICORN_BIND} --workers ${FRONTEND_WORKERS} --threads ${FRONTEND_THREADS} --worker-class ${GUNICORN_WORKER_CLASS} --max-requests ${GUNICORN_MAX_REQUESTS} --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER} --timeout ${GUNICORN_TIMEOUT} --access-logfile - --error-logfile - app.app:flask"]