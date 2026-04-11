from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import traceback
import uuid
from config import Config
from models.db import init_db, save_upload, save_analysis, get_all_uploads, get_analysis_by_upload
from utils.helpers import allowed_file, read_file, clean_data, auto_detect_columns, detect_currency
from analysis.elasticity import calculate_elasticity
from analysis.optimal_price import calculate_optimal_price
from analysis.competitor import compare_competitors
from analysis.simulator import simulate_discount, simulate_bundling

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": "*"}})

init_db()
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

session_store = {}


def get_upload_context():
    payload = request.get_json(silent=True) or {}
    upload_token = (
        request.headers.get('X-Upload-Token')
        or request.args.get('upload_token')
        or payload.get('upload_token')
    )

    if not upload_token:
        return None, None, (jsonify({'error': 'Missing upload token. Please upload a file first'}), 400)

    context = session_store.get(upload_token)
    if not context:
        return None, None, (jsonify({'error': 'Upload session expired or was not found'}), 404)

    return context, upload_token, None


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
        auto_mapping = auto_detect_columns(list(df.columns))
        price_col = auto_mapping.get('price') or list(df.columns)[0]
        currency = detect_currency(df, price_col)

        upload_token = str(uuid.uuid4())
        session_store[upload_token] = {
            'data': df,
            'filepath': filepath,
            'filename': file.filename,
            'currency': currency,
        }

        return jsonify({
            'message': 'File uploaded successfully',
            'rows': len(df),
            'columns': list(df.columns),
            'auto_mapping': auto_mapping,
            'currency': currency,
            'upload_token': upload_token,
        })

    except Exception as e:
        print('UPLOAD ERROR:', traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        context, upload_token, error = get_upload_context()
        if error:
            return error

        mapping = request.get_json() or {}
        price_col = mapping.get('price')
        units_col = mapping.get('units_sold')
        competitor_col = mapping.get('competitor_price')
        date_col = mapping.get('date')

        if not all([price_col, units_col, competitor_col]):
            return jsonify({'error': 'Please map all required columns'}), 400

        df = context['data'].copy()
        rename_map = {
            price_col: 'price',
            units_col: 'units_sold',
            competitor_col: 'competitor_price',
        }
        if date_col:
            rename_map[date_col] = 'date'

        df = df.rename(columns=rename_map)
        context['mapped'] = df

        elasticity_result = calculate_elasticity(df)
        optimal_result = calculate_optimal_price(df)
        competitor_result = compare_competitors(df)

        upload_id = save_upload(context['filename'], context['filepath'])
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

        context['upload_id'] = upload_id
        context['product_name'] = mapping.get('product_name', 'Your Product')

        return jsonify({
            'message': 'Analysis complete',
            'upload_id': upload_id,
            'upload_token': upload_token,
            'elasticity': elasticity_result,
            'optimal_price': optimal_result,
            'competitor': competitor_result,
            'currency': context.get('currency', {'symbol': '$', 'code': 'USD', 'name': 'US Dollar'}),
            'product_name': context.get('product_name', 'Your Product'),
        })

    except Exception as e:
        print('ANALYZE ERROR:', traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/elasticity', methods=['GET'])
def elasticity():
    context, _, error = get_upload_context()
    if error:
        return error
    if 'mapped' not in context:
        return jsonify({'error': 'Please upload and analyze a file first'}), 400
    return jsonify(calculate_elasticity(context['mapped']))


@app.route('/optimal-price', methods=['GET'])
def optimal_price():
    context, _, error = get_upload_context()
    if error:
        return error
    if 'mapped' not in context:
        return jsonify({'error': 'Please upload and analyze a file first'}), 400
    return jsonify(calculate_optimal_price(context['mapped']))


@app.route('/competitor', methods=['GET'])
def competitor():
    context, _, error = get_upload_context()
    if error:
        return error
    if 'mapped' not in context:
        return jsonify({'error': 'Please upload and analyze a file first'}), 400
    return jsonify(compare_competitors(context['mapped']))


@app.route('/simulate', methods=['POST'])
def simulate():
    context, _, error = get_upload_context()
    if error:
        return error
    if 'mapped' not in context:
        return jsonify({'error': 'Please upload and analyze a file first'}), 400

    data = request.get_json() or {}
    simulation_type = data.get('type')

    if simulation_type == 'discount':
        result = simulate_discount(
            context['mapped'],
            data.get('discount_pct', 10),
            data.get('elasticity', -1),
        )
    elif simulation_type == 'bundling':
        result = simulate_bundling(
            context['mapped'],
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


if __name__ == '__main__':
    app.run(debug=True, port=5000)
