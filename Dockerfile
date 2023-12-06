# Base image
FROM python:3.9

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

# Copy streamlit files
COPY streamlit-files-local /app/streamlit-files-local

# Expose port 8501 for http traffic
EXPOSE 8501

# See everything (in a linux container)...
RUN ls -R

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Set the command to run the Streamlit application
CMD ["streamlit", "run", "--server.port=8501", "--server.fileWatcherType=none", "streamlit-files-local/Welcome.py"]