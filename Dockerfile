# Use official Python slim image
FROM python:3.9-slim

# Set working directory inside container to app folder
WORKDIR /app/airbnb_price_app

# Copy requirements.txt if you have it in root (optional)
COPY airbnb_price_app/requirements.txt /app/
RUN pip install -r /app/requirements.txt
RUN pip install --upgrade pip



# Copy all contents from airbnb_price_app into working directory
COPY airbnb_price_app/. /app/airbnb_price_app/

# Expose port your app runs on (usually 5000 for Flask)
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
