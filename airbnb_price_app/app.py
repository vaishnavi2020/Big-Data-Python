from flask import Flask, render_template, request, jsonify, send_file
import pickle
import pandas as pd
import numpy as np
import os
import json

app = Flask(__name__)

# Load model and feature list once on startup
with open(os.path.join('model', 'best_model.pkl'), 'rb') as f:
    model = pickle.load(f)

with open(os.path.join('model', 'model_features.pkl'), 'rb') as f:
    model_features = pickle.load(f)

# Load and preprocess dataset once (to avoid reloading on every request)
df = pd.read_csv('merged_data.csv')
df['price'] = df['price'].replace(r'[\$,]', '', regex=True).astype(float)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict_price', methods=['POST'])
def predict_price():
    try:
        data = request.get_json()

        # Parse and convert inputs
        neighbourhood = data['neighbourhood']
        room_type = data['room_type']
        minimum_nights = int(data['minimum_nights'])
        number_of_reviews = int(data['number_of_reviews'])
        reviews_per_month = float(data['reviews_per_month'])

        # Filter similar listings with loose criteria
        filtered = df[
            (df['neighbourhood_cleansed'] == neighbourhood) &
            (df['room_type'] == room_type) &
            (df['minimum_nights'].between(minimum_nights - 1, minimum_nights + 1)) &
            (df['number_of_reviews'].between(number_of_reviews - 2, number_of_reviews + 2)) &
            (df['reviews_per_month'].between(reviews_per_month - 1, reviews_per_month + 1))
        ]

        actual_avg_price = filtered['price'].mean() if len(filtered) > 0 else None

        # Prepare input dictionary with one-hot encoding for categorical variables
        input_dict = {
            'minimum_nights': minimum_nights,
            'number_of_reviews': number_of_reviews,
            'reviews_per_month': reviews_per_month,
            **{f"room_type_{room_type}": 1},
            **{f"neighbourhood_cleansed_{neighbourhood}": 1},
        }

        # Fill zero for other features expected by the model
        for feat in model_features:
            if feat not in input_dict:
                input_dict[feat] = 0

        # Create input DataFrame with columns in the right order
        input_df = pd.DataFrame([input_dict], columns=model_features)

        # Predict log(price)
        log_pred = model.predict(input_df)[0]
        predicted_price = np.expm1(log_pred)  # revert log1p

        return jsonify({
            'actual_avg_price': round(actual_avg_price, 2) if actual_avg_price else None,
            'log_predicted_price': round(log_pred, 4),
            'predicted_price': round(predicted_price, 2),
            'neighbourhood': neighbourhood
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
        return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('utf-8').lower().strip()
    nbhs = [f.split("neighbourhood_cleansed_")[1] for f in model_features if f.startswith("neighbourhood_cleansed_")]
    nbhs_norm = list({normalize(n): n for n in nbhs}.values())  # unique normalized
    return jsonify(sorted(nbhs_norm))

@app.route('/api/listings')
def get_listings():
    import math
    with open('static/listings.json', 'r', encoding='utf-8') as f:
        listings = json.load(f)
        filtered = [d for d in listings if 'price' in d and isinstance(d['price'], (int, float)) and not math.isnan(d['price'])]
    return jsonify(filtered)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
