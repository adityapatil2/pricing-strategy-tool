from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
from config import Config
from models.db import init_db, save_upload, save_analysis, get_all_uploads, get_analysis_by_upload
from utils.helpers import allowed_file, read_file, clean_data
from analysis.elasticity import calculate_elasticity
from analysis.optimal_price import calculate_optimal_price
from analysis.competitor import compare_competitors
from analysis.simulator import simulate_discount, simulate_bundling

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=Config.CORS_ORIGINS)

# Initialize database
init_db()

# Store dataframe and column mapping in memory
current_df = {}

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Pricing Strategy API is running!"})


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print("Files received:", request.files)

        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
            return jsonify({"error": "Only CSV and Excel files allowed"}), 400

        # Save file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Read file
        df = read_file(filepath)
        df = clean_data(df)

        # Store in memory
        current_df['data'] = df
        current_df['filepath'] = filepath
        current_df['filename'] = file.filename

        # Return columns to frontend for mapping
        return jsonify({
            "message": "File uploaded successfully",
            "rows": len(df),
            "columns": list(df.columns)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'data' not in current_df:
            return jsonify({"error": "Please upload a file first"}), 400

        # Get column mapping from frontend
        mapping = request.get_json()
        price_col = mapping.get('price')
        units_col = mapping.get('units_sold')
        competitor_col = mapping.get('competitor_price')
        date_col = mapping.get('date')

        # Validate mapping
        if not all([price_col, units_col, competitor_col]):
            return jsonify({"error": "Please map all required columns"}), 400

        # Get dataframe and rename columns
        df = current_df['data'].copy()
        rename_map = {
            price_col: 'price',
            units_col: 'units_sold',
            competitor_col: 'competitor_price'
        }
        if date_col:
            rename_map[date_col] = 'date'

        df = df.rename(columns=rename_map)

        # Store mapped dataframe
        current_df['mapped'] = df

        # Run all analysis
        elasticity_result = calculate_elasticity(df)
        optimal_result = calculate_optimal_price(df)
        competitor_result = compare_competitors(df)

        # Save to database
        upload_id = save_upload(
            current_df['filename'],
            current_df['filepath']
        )
        save_analysis(
            upload_id=upload_id,
            elasticity=elasticity_result.get('elasticity'),
            optimal_price=optimal_result.get('optimal_price'),
            current_price=optimal_result.get('current_price'),
            current_revenue=optimal_result.get('current_revenue'),
            projected_revenue=optimal_result.get('optimal_revenue'),
            competitor_avg_price=competitor_result.get('competitor_avg_price'),
            price_difference_pct=competitor_result.get('price_difference_pct')
        )

        current_df['upload_id'] = upload_id

        return jsonify({
            "message": "Analysis complete",
            "upload_id": upload_id,
            "elasticity": elasticity_result,
            "optimal_price": optimal_result,
            "competitor": competitor_result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/elasticity', methods=['GET'])
def elasticity():
    if 'mapped' not in current_df:
        return jsonify({"error": "Please upload and analyze a file first"}), 400
    result = calculate_elasticity(current_df['mapped'])
    return jsonify(result)


@app.route('/optimal-price', methods=['GET'])
def optimal_price():
    if 'mapped' not in current_df:
        return jsonify({"error": "Please upload and analyze a file first"}), 400
    result = calculate_optimal_price(current_df['mapped'])
    return jsonify(result)


@app.route('/competitor', methods=['GET'])
def competitor():
    if 'mapped' not in current_df:
        return jsonify({"error": "Please upload and analyze a file first"}), 400
    result = compare_competitors(current_df['mapped'])
    return jsonify(result)


@app.route('/simulate', methods=['POST'])
def simulate():
    if 'mapped' not in current_df:
        return jsonify({"error": "Please upload and analyze a file first"}), 400

    data = request.get_json()
    simulation_type = data.get('type')

    if simulation_type == 'discount':
        discount_pct = data.get('discount_pct', 10)
        elasticity = data.get('elasticity', -1)
        result = simulate_discount(current_df['mapped'], discount_pct, elasticity)

    elif simulation_type == 'bundling':
        bundle_discount_pct = data.get('bundle_discount_pct', 10)
        result = simulate_bundling(current_df['mapped'], bundle_discount_pct)

    else:
        return jsonify({"error": "Invalid simulation type"}), 400

    return jsonify(result)


@app.route('/history', methods=['GET'])
def history():
    uploads = get_all_uploads()
    return jsonify(uploads)


@app.route('/history/<int:upload_id>', methods=['GET'])
def history_detail(upload_id):
    result = get_analysis_by_upload(upload_id)
    if not result:
        return jsonify({"error": "No analysis found for this upload"}), 404
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=5000)