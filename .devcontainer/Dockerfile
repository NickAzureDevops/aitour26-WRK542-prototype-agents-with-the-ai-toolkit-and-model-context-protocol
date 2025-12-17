FROM mcr.microsoft.com/devcontainers/python:3.13-bookworm

# Install SQLite3
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.13
RUN python -m pip install --upgrade pip

# Copy the shared library first so it's available for the editable install
COPY shared /workspace/shared

# Install the packages required to run the workshop as a student
COPY requirements.lock.txt /workspace/
WORKDIR /workspace
RUN pip install -r requirements.lock.txt
