FROM mcr.microsoft.com/devcontainers/python:3.13-bookworm

# Install SQLite3
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.13
RUN python -m pip install --upgrade pip

# Install the packages required to run the workshop as a student
COPY requirements.lock.txt .
RUN pip install -r requirements.lock.txt

# Install the shared library in editable mode
COPY shared /workspace/shared
RUN pip install -e /workspace/shared
