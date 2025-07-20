from flask import Flask, render_template, request, jsonify, send_file
import pickle
import pandas as pd
import os
import json

app = Flask(__name__)

# Load model and feature list
with open(os.path.join('model', 'best_model.pkl'), 'rb') as f:
    model = pickle.load(f)

with open(os.path.join('model', 'model_features.pkl'), 'rb') as f:
    model_features = pickle.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict_price', methods=['POST'])
def predict_price():
    try:
        data = request.get_json()

        # Base numeric inputs
        input_data = {
            'minimum_nights': int(data['minimum_nights']),
            'number_of_reviews': int(data['number_of_reviews']),
            'reviews_per_month': float(data['reviews_per_month']),
        }

        # Add room_type one-hot if available in features
        room_col = f"room_type_{data['room_type']}"
        if room_col in model_features:
            input_data[room_col] = 1

        # Add neighbourhood one-hot if available in features
        nbh_col = f"neighbourhood_cleansed_{data['neighbourhood']}"
        if nbh_col in model_features:
            input_data[nbh_col] = 1

        # Create complete input DataFrame
        input_df = pd.DataFrame([input_data], columns=model_features).fillna(0)

        prediction = model.predict(input_df)[0]
        return jsonify({
            'predicted_price': round(prediction, 2),
            'neighbourhood': data['neighbourhood']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/geojson')
def geojson():
    return send_file("static/neighbourhoods.geojson")

@app.route('/api/neighbourhoods')
def get_neighbourhoods():
    import unicodedata
    # Extract valid neighbourhoods from model features
    def normalize(s):
        # Remove accents, lowercase, strip spaces
        return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('utf-8').lower().strip()
    nbhs = [f.split("neighbourhood_cleansed_")[1] for f in model_features if f.startswith("neighbourhood_cleansed_")]
    nbhs_norm = list({normalize(n): n for n in nbhs}.values())  # unique normalized
    return jsonify(sorted(nbhs_norm))

@app.route('/api/listings')
def get_listings():
    import math
    with open('static/listings.json', 'r', encoding='utf-8') as f:
        listings = json.load(f)
        # Filter out listings with invalid price
        filtered = [d for d in listings if 'price' in d and isinstance(d['price'], (int, float)) and not math.isnan(d['price'])]
    return jsonify(filtered)

if __name__ == "__main__":
    app.run(debug=True)
