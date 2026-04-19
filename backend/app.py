from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import traceback
import pandas as pd
from config import Config
from models.db import init_db, save_upload, save_analysis, get_all_uploads, get_analysis_by_upload
from utils.helpers import allowed_file, read_file, clean_data, auto_detect_columns, detect_currency
from analysis.elasticity import calculate_elasticity
from analysis.optimal_price import calculate_optimal_price
from analysis.competitor import compare_competitors
from analysis.simulator import simulate_discount, simulate_bundling
from analysis.price_predictor import predict_optimal_price
from analysis.demand_forecaster import forecast_demand
from analysis.revenue_forecaster import forecast_revenue

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": "*"}})

init_db()
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Simple in-memory store
current_df = {}

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Pricing Strategy API is running!'})


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
            return jsonify({'error': 'Only CSV and Excel files allowed'}), 400

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        df = clean_data(read_file(filepath))
        auto_mapping = auto_detect_columns(list(df.columns)) or {}
        price_col = auto_mapping.get('price') or list(df.columns)[0]
        currency = detect_currency(df, price_col)

        current_df['data'] = df
        current_df['filepath'] = filepath
        current_df['filename'] = file.filename
        current_df['currency'] = currency

        return jsonify({
            'message': 'File uploaded successfully',
            'rows': len(df),
            'columns': list(df.columns),
            'auto_mapping': auto_mapping,
            'currency': currency,
        })

    except Exception as e:
        print('UPLOAD ERROR:', traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        if 'data' not in current_df:
            return jsonify({'error': 'Please upload a file first'}), 400

        mapping = request.get_json() or {}
        price_col = mapping.get('price')
        units_col = mapping.get('units_sold')
        competitor_col = mapping.get('competitor_price')
        date_col = mapping.get('date')

        if not all([price_col, units_col, competitor_col]):
            return jsonify({'error': 'Please map all required columns'}), 400

        df = current_df['data'].copy()
        rename_map = {
            price_col: 'price',
            units_col: 'units_sold',
            competitor_col: 'competitor_price',
        }
        if date_col:
            rename_map[date_col] = 'date'

        df = df.rename(columns=rename_map)
        current_df['mapped'] = df

        elasticity_result = calculate_elasticity(df)
        optimal_result = calculate_optimal_price(df)
        competitor_result = compare_competitors(df)

        upload_id = save_upload(current_df['filename'], current_df['filepath'])
        save_analysis(
            upload_id=upload_id,
            elasticity=elasticity_result.get('elasticity'),
            optimal_price=optimal_result.get('optimal_price'),
            current_price=optimal_result.get('current_price'),
            current_revenue=optimal_result.get('current_revenue'),
            projected_revenue=optimal_result.get('optimal_revenue'),
            competitor_avg_price=competitor_result.get('competitor_avg_price'),
            price_difference_pct=competitor_result.get('price_difference_pct'),
        )

        current_df['upload_id'] = upload_id
        current_df['product_name'] = mapping.get('product_name', 'Your Product')

        return jsonify({
            'message': 'Analysis complete',
            'upload_id': upload_id,
            'elasticity': elasticity_result,
            'optimal_price': optimal_result,
            'competitor': competitor_result,
            'currency': current_df.get('currency', {'symbol': '$', 'code': 'USD', 'name': 'US Dollar'}),
            'product_name': current_df.get('product_name', 'Your Product'),
        })

    except Exception as e:
        print('ANALYZE ERROR:', traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/elasticity', methods=['GET'])
def elasticity():
    if 'mapped' not in current_df:
        return jsonify({'error': 'Please upload and analyze a file first'}), 400
    return jsonify(calculate_elasticity(current_df['mapped']))


@app.route('/optimal-price', methods=['GET'])
def optimal_price():
    if 'mapped' not in current_df:
        return jsonify({'error': 'Please upload and analyze a file first'}), 400
    return jsonify(calculate_optimal_price(current_df['mapped']))


@app.route('/competitor', methods=['GET'])
def competitor():
    if 'mapped' not in current_df:
        return jsonify({'error': 'Please upload and analyze a file first'}), 400
    return jsonify(compare_competitors(current_df['mapped']))


@app.route('/simulate', methods=['POST'])
def simulate():
    if 'mapped' not in current_df:
        return jsonify({'error': 'Please upload and analyze a file first'}), 400

    data = request.get_json() or {}
    simulation_type = data.get('type')

    if simulation_type == 'discount':
        result = simulate_discount(
            current_df['mapped'],
            data.get('discount_pct', 10),
            data.get('elasticity', -1),
        )
    elif simulation_type == 'bundling':
        result = simulate_bundling(
            current_df['mapped'],
            data.get('bundle_discount_pct', 10),
        )
    else:
        return jsonify({'error': 'Invalid simulation type'}), 400

    return jsonify(result)


@app.route('/history', methods=['GET'])
def history():
    return jsonify(get_all_uploads())


@app.route('/history/<int:upload_id>', methods=['GET'])
def history_detail(upload_id):
    result = get_analysis_by_upload(upload_id)
    if not result:
        return jsonify({'error': 'No analysis found for this upload'}), 404
    return jsonify(result)


@app.route('/ml/price-predictor', methods=['GET'])
def ml_price_predictor():
    if 'mapped' not in current_df:
        return jsonify({"error": "Please upload and analyze a file first"}), 400
    result = predict_optimal_price(current_df['mapped'])
    return jsonify(result)


@app.route('/ml/demand-forecaster', methods=['GET'])
def ml_demand_forecaster():
    if 'mapped' not in current_df:
        return jsonify({"error": "Please upload and analyze a file first"}), 400
    result = forecast_demand(current_df['mapped'])
    return jsonify(result)


@app.route('/ml/revenue-forecaster', methods=['GET'])
def ml_revenue_forecaster():
    if 'mapped' not in current_df:
        return jsonify({"error": "Please upload and analyze a file first"}), 400
    result = forecast_revenue(current_df['mapped'])
    return jsonify(result)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)