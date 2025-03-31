FROM python:3.11-bullseye

# Installing/Updating system dependencies
RUN apt update -y && \
    apt install postgresql git curl -y --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install rust toolchain
RUN curl -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Update pip
RUN pip install --upgrade pip

WORKDIR /stern

# Install uwsgi for deployment
RUN pip install uwsgi

# Install python dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Get config for deployment
ARG FRONTEND_WORKERS=4
ENV FRONTEND_WORKERS $FRONTEND_WORKERS

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

CMD uwsgi --http 0.0.0.0:80 \
          --ini uwsgi.ini \
          -w app:flask \
          --lazy