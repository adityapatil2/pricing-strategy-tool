import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'pricing.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Create uploads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create analysis results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_id INTEGER,
            elasticity REAL,
            optimal_price REAL,
            current_price REAL,
            current_revenue REAL,
            projected_revenue REAL,
            competitor_avg_price REAL,
            price_difference_pct REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (upload_id) REFERENCES uploads (id)
        )
    ''')

    conn.commit()
    conn.close()

def save_upload(filename, filepath):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO uploads (filename, filepath)
        VALUES (?, ?)
    ''', (filename, filepath))
    conn.commit()
    upload_id = cursor.lastrowid
    conn.close()
    return upload_id

def save_analysis(upload_id, elasticity, optimal_price, current_price,
                  current_revenue, projected_revenue,
                  competitor_avg_price, price_difference_pct):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO analysis_results (
            upload_id, elasticity, optimal_price, current_price,
            current_revenue, projected_revenue,
            competitor_avg_price, price_difference_pct
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (upload_id, elasticity, optimal_price, current_price,
          current_revenue, projected_revenue,
          competitor_avg_price, price_difference_pct))
    conn.commit()
    conn.close()

def get_all_uploads():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM uploads ORDER BY uploaded_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_analysis_by_upload(upload_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM analysis_results
        WHERE upload_id = ?
        ORDER BY created_at DESC LIMIT 1
    ''', (upload_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None