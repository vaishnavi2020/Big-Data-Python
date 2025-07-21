FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY airbnb_price_app/ ./airbnb_price_app/

WORKDIR /app/airbnb_price_app

EXPOSE 5000

CMD ["python", "app.py"]
