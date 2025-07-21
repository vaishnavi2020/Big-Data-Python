# Use official Python slim image
FROM python:3.9-slim

# Set working directory inside container
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements file and install dependencies
COPY airbnb_price_app/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Copy entire app into container
COPY airbnb_price_app/ ./

# Expose the Flask port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
