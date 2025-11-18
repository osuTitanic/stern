FROM python:3.14-alpine AS builder

ENV PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

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

# Install Python dependencies (including uwsgi) into a relocatable prefix
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --no-compile --root /install -r requirements.txt uwsgi

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
ARG UWSGI_OFFLOAD_THREADS=4
ARG UWSGI_STATS=":1717"
ARG UWSGI_CHEAPER_MIN=2
ARG UWSGI_CHEAPER_INITIAL=2
ARG UWSGI_CHEAPER_OVERLOAD=6
ARG UWSGI_CHEAPER_STEP=1

ENV FRONTEND_WORKERS=${FRONTEND_WORKERS} \
    FRONTEND_THREADS=${FRONTEND_THREADS} \
    UWSGI_OFFLOAD_THREADS=${UWSGI_OFFLOAD_THREADS} \
    UWSGI_STATS=${UWSGI_STATS} \
    UWSGI_CHEAPER_MIN=${UWSGI_CHEAPER_MIN} \
    UWSGI_CHEAPER_INITIAL=${UWSGI_CHEAPER_INITIAL} \
    UWSGI_CHEAPER_OVERLOAD=${UWSGI_CHEAPER_OVERLOAD} \
    UWSGI_CHEAPER_STEP=${UWSGI_CHEAPER_STEP}

WORKDIR /stern

# Copy only the installed packages from the builder layer
COPY --from=builder /install/usr/local /usr/local

# Copy application source
COPY . .

# Copy tuned uwsgi configuration
COPY uwsgi.ini ./uwsgi.ini

# Precompile python files for faster startup
RUN python -m compileall -q app

STOPSIGNAL SIGQUIT
ENTRYPOINT ["/sbin/tini", "--"]

CMD ["uwsgi", "--ini", "uwsgi.ini"]