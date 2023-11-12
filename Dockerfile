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

# Install python dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Install pyuwsgi for deployment
RUN pip install pyuwsgi

# Copy source code
COPY . .

# Get config for deployment
ENV FRONTEND_HOST $FRONTEND_HOST
ENV FRONTEND_PORT $FRONTEND_PORT

EXPOSE $FRONTEND_PORT

CMD uwsgi --http 0.0.0.0:80 \
          -w app:flask \
          --master