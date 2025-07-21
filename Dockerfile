# Dockerfile (in Big-Data-Python/)
FROM python:3.10

WORKDIR /app

# Copy app folder contents into container
COPY airbnb_price_app/ /app/

# Copy requirements.txt
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
