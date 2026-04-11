import pandas as pd


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def read_file(filepath):
    ext = filepath.rsplit('.', 1)[1].lower()
    if ext == 'csv':
        return pd.read_csv(filepath)
    if ext == 'xlsx':
        return pd.read_excel(filepath)
    raise ValueError('Unsupported file type')


def clean_data(df):
    df = df.drop_duplicates()
    df = df.dropna()
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    return df


def validate_columns(df, required_columns):
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        return False, f"Missing columns: {', '.join(missing)}"
    return True, 'OK'


def auto_detect_columns(columns):
    mapping = {
        'price': None,
        'units_sold': None,
        'competitor_price': None,
        'date': None,
    }

    price_keywords = ['price', 'selling_price', 'unit_price', 'amount', 'cost', 'rate']
    units_keywords = ['units_sold', 'units', 'quantity', 'qty', 'sales', 'demand', 'sold', 'volume']
    competitor_keywords = ['competitor_price', 'comp_price', 'market_price', 'rival_price', 'competition']
    date_keywords = ['date', 'timestamp', 'day', 'period', 'time', 'month']

    for col in columns:
        col_lower = col.lower()

        if mapping['price'] is None and any(keyword in col_lower for keyword in price_keywords):
            mapping['price'] = col

        if mapping['units_sold'] is None and any(keyword in col_lower for keyword in units_keywords):
            mapping['units_sold'] = col

        if mapping['competitor_price'] is None and any(keyword in col_lower for keyword in competitor_keywords):
            mapping['competitor_price'] = col

        if mapping['date'] is None and any(keyword in col_lower for keyword in date_keywords):
            mapping['date'] = col

    return mapping


def detect_currency(df, price_col='price'):
    try:
        col_names = ' '.join(df.columns.tolist()).lower()

        if 'inr' in col_names or 'rupee' in col_names or 'rs' in col_names:
            return {'symbol': 'Rs', 'code': 'INR', 'name': 'Indian Rupee'}
        if 'usd' in col_names or 'dollar' in col_names:
            return {'symbol': '$', 'code': 'USD', 'name': 'US Dollar'}
        if 'eur' in col_names or 'euro' in col_names:
            return {'symbol': 'EUR', 'code': 'EUR', 'name': 'Euro'}
        if 'gbp' in col_names or 'pound' in col_names:
            return {'symbol': 'GBP', 'code': 'GBP', 'name': 'British Pound'}
        if 'jpy' in col_names or 'yen' in col_names:
            return {'symbol': 'JPY', 'code': 'JPY', 'name': 'Japanese Yen'}

        if price_col in df.columns:
            price_str = df[price_col].astype(str).str.cat()
            price_str_lower = price_str.lower()

            if '\u20B9' in price_str or 'rs' in price_str_lower:
                return {'symbol': 'Rs', 'code': 'INR', 'name': 'Indian Rupee'}
            if '$' in price_str or 'usd' in price_str_lower:
                return {'symbol': '$', 'code': 'USD', 'name': 'US Dollar'}
            if '\u20AC' in price_str or 'eur' in price_str_lower:
                return {'symbol': 'EUR', 'code': 'EUR', 'name': 'Euro'}
            if '\u00A3' in price_str or 'gbp' in price_str_lower:
                return {'symbol': 'GBP', 'code': 'GBP', 'name': 'British Pound'}
            if '\u00A5' in price_str or 'jpy' in price_str_lower:
                return {'symbol': 'JPY', 'code': 'JPY', 'name': 'Japanese Yen'}

            avg_price = df[price_col].mean()
            if avg_price > 500:
                return {'symbol': 'Rs', 'code': 'INR', 'name': 'Indian Rupee'}
            return {'symbol': '$', 'code': 'USD', 'name': 'US Dollar'}

    except Exception:
        pass

    return {'symbol': '$', 'code': 'USD', 'name': 'US Dollar'}
