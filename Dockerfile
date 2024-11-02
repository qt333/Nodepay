FROM python:3.9-slim

# Set environment variables
ENV EXTENSION_ID=lgmpfmgeabnnlemejacfljbmonaomfmm
ENV EXTENSION_URL='https://app.nodepay.ai/'
ENV GIT_USERNAME=warren-bank
ENV GIT_REPO=chrome-extension-downloader

# Install necessary packages and clean up to reduce image size
RUN apt-get update && \
    apt-get install -qqy --no-install-recommends \
    curl \
    wget \
    git \
    chromium \
    chromium-driver \
    python3-pip \
    python3-requests \
    python3-selenium \
    coreutils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download crx downloader from git
RUN git clone --depth 1 "https://github.com/${GIT_USERNAME}/${GIT_REPO}.git" && \
    chmod +x ./${GIT_REPO}/bin/*

# Download the extension selected
RUN ./${GIT_REPO}/bin/crxdl $EXTENSION_ID

# Install only required Python packages
RUN pip install --no-cache-dir selenium requests

# Copy the Python script
COPY main.py .

# Run the Python script
ENTRYPOINT [ "python", "main.py" ]