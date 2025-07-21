# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the app source code and model folder
COPY app.py .
COPY model/ ./model/

# Expose port if needed (e.g., Flask default port 5000)
EXPOSE 5000

# Command to run the app
CMD ["python", "app.py"]
