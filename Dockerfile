# Base image
FROM python:3.9-slim

# Maintainer information
LABEL maintainer="Amazon Capstone: Graph LLM"

# Set working directory
WORKDIR /app

# Copy requirements for virtual environment
COPY requirements.txt .

# Install virtual environment
RUN pip install -r requirements.txt

# Copy src modules
COPY src /app/src

# Copy config
COPY config /app/config

# Copy plots
COPY plots /app/plots

# Copy streamlit files
COPY streamlit-files-local /app/streamlit-files-local

# Expose port 8501 for http traffic
EXPOSE 8501

# Set the command to run the Streamlit application
CMD ["streamlit", "run", "--server.port=8501", "--server.fileWatcherType=none", "streamlit-files-local/Welcome.py"]