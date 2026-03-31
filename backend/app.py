from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
from config import Config
from models.db import init_db, save_upload, save_analysis, get_all_uploads, get_analysis_by_upload
from utils.helpers import allowed_file, read_file, clean_data, validate_columns
from analysis.elasticity import calculate_elasticity
from analysis.optimal_price import calculate_optimal_price
from analysis.competitor import compare_competitors
from analysis.simulator import simulate_discount, simulate_bundling

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=Config.CORS_ORIGINS)

# Initialize database
init_db()

# Required columns in uploaded CSV
REQUIRED_COLUMNS = ['price', 'units_sold', 'competitor_price']

# Store dataframe in memory temporarily
current_df = {}

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Pricing Strategy API is running!"})

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print("Files received:", request.files)
        print("Form data:", request.form)

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

        # Read and clean data
        df = read_file(filepath)
        df = clean_data(df)

        # Validate columns
        is_valid, message = validate_columns(df, REQUIRED_COLUMNS)
        if not is_valid:
            return jsonify({"error": message}), 400

        # Save upload to database
        upload_id = save_upload(file.filename, filepath)

        # Run all analysis
        elasticity_result = calculate_elasticity(df)
        optimal_result = calculate_optimal_price(df)
        competitor_result = compare_competitors(df)

        # Save analysis results to database
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

        # Store in memory
        current_df['data'] = df
        current_df['upload_id'] = upload_id

        return jsonify({
            "message": "File uploaded successfully",
            "upload_id": upload_id,
            "rows": len(df),
            "columns": list(df.columns)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/elasticity', methods=['GET'])
def elasticity():
    if 'data' not in current_df:
        return jsonify({"error": "Please upload a file first"}), 400
    result = calculate_elasticity(current_df['data'])
    return jsonify(result)


@app.route('/optimal-price', methods=['GET'])
def optimal_price():
    if 'data' not in current_df:
        return jsonify({"error": "Please upload a file first"}), 400
    result = calculate_optimal_price(current_df['data'])
    return jsonify(result)


@app.route('/competitor', methods=['GET'])
def competitor():
    if 'data' not in current_df:
        return jsonify({"error": "Please upload a file first"}), 400
    result = compare_competitors(current_df['data'])
    return jsonify(result)


@app.route('/simulate', methods=['POST'])
def simulate():
    if 'data' not in current_df:
        return jsonify({"error": "Please upload a file first"}), 400

    data = request.get_json()
    simulation_type = data.get('type')

    if simulation_type == 'discount':
        discount_pct = data.get('discount_pct', 10)
        elasticity = data.get('elasticity', -1)
        result = simulate_discount(current_df['data'], discount_pct, elasticity)

    elif simulation_type == 'bundling':
        bundle_discount_pct = data.get('bundle_discount_pct', 10)
        result = simulate_bundling(current_df['data'], bundle_discount_pct)

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