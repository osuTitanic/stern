FROM python:3.11-bullseye

# Installing/Updating system dependencies
RUN apt update -y
RUN apt install postgresql git curl -y

# Install rust toolchain
RUN curl -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Update pip
RUN pip install --upgrade pip

WORKDIR /stern

# Somehow this doesn't work as a command-line argument, so
# we have to write it to a configuration file...
RUN echo "[uwsgi]max-requests-delta = 1000" > uwsgi.ini

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

CMD uwsgi --http 0.0.0.0:80 \
          --ini uwsgi.ini \
          -p ${FRONTEND_WORKERS} \
          -w app:flask \
          --max-requests 180000 \
          --enable-threads \
          --lazy-apps