FROM python:3.13-slim-bullseye AS builder

# Installing build dependencies
RUN apt update -y && \
    apt install -y --no-install-recommends \
        postgresql-client \
        git \
        curl \
        build-essential \
        gcc \
        python3-dev \
        libpcre3-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install rust toolchain
RUN curl -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install python dependencies
# & uwsgi for deployment
WORKDIR /stern
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uwsgi

FROM python:3.13-slim-bullseye

# Install runtime dependencies only
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /stern

# Copy installed Python packages from builder
COPY --from=builder /usr/local /usr/local
COPY --from=builder /stern /stern

# Copy source code
COPY . .

# Generate __pycache__ directories
ENV PYTHONDONTWRITEBYTECODE=1
RUN python -m compileall -q app

# Get config for deployment
ARG FRONTEND_WORKERS=4
ENV FRONTEND_WORKERS $FRONTEND_WORKERS

# Disable output buffering
ENV PYTHONUNBUFFERED=1

RUN echo " \
[uwsgi] \n \
max-requests-delta = 1000 \n \
reload-on-rss = 312 \n \
processes = ${FRONTEND_WORKERS} \n \
max-requests = 150000 \n \
cheaper = 2 \n \
cheaper-initial = 2 \n \
cheaper-overload = 6 \n \
" > uwsgi.ini

CMD ["uwsgi", "--http", "0.0.0.0:80", "--ini", "uwsgi.ini", "-w", "app:flask", "--lazy"]