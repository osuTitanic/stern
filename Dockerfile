FROM python:3.14-alpine AS builder

ENV PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies for Python wheels and uwsgi modules
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

# Install Python dependencies into a relocatable prefix
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install --no-compile --root /install -r requirements.txt granian[pname,uvloop]

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

ENV FRONTEND_WORKERS=${FRONTEND_WORKERS} \
    FRONTEND_THREADS=${FRONTEND_THREADS}

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

CMD ["/bin/sh", "-c", "granian --host 0.0.0.0 --port 80 --interface wsgi --workers ${FRONTEND_WORKERS} --runtime-threads ${FRONTEND_THREADS} --loop uvloop --http 1 --no-ws --backpressure 128 --respawn-failed-workers --access-log --process-name deck-worker --workers-kill-timeout 5 --workers-lifetime 43200 --workers-max-rss 512 app:flask"]