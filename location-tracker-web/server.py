from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)  # Allow cross-origin requests if needed

DB_PATH = 'locations.db'

def init_db():
    """Initialize the SQLite database to store locations."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS location_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            user_agent TEXT,
            ip_address TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

@app.route('/')
def serve_index():
    """Serve the main tracking page"""
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def serve_css():
    """Serve the CSS file"""
    return send_from_directory('.', 'style.css')

@app.route('/script.js')
def serve_js():
    """Serve the JavaScript file"""
    return send_from_directory('.', 'script.js')

@app.route('/api/save-location', methods=['POST'])
def save_location():
    """Endpoint to receive location data from the frontend"""
    data = request.json
    
    lat = data.get('lat')
    lng = data.get('lng')
    
    if not lat or not lng:
        return jsonify({'status': 'error', 'message': 'Missing coordinates'}), 400

    # Also grab some metadata for the dashboard
    user_agent = request.headers.get('User-Agent', 'Unknown')
    # Use X-Forwarded-For if behind ngrok, otherwise remote_addr
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO location_data (latitude, longitude, user_agent, ip_address) VALUES (?, ?, ?, ?)',
            (lat, lng, user_agent, ip_address)
        )
        conn.commit()
        conn.close()
        
        print(f"✅ NEW LOCATION SAVED! -> Lat: {lat}, Lng: {lng} from IP: {ip_address}")
        return jsonify({'status': 'success', 'message': 'Location saved securely'}), 200
        
    except Exception as e:
        print(f"Error saving location: {e}")
        return jsonify({'status': 'error', 'message': 'Database error'}), 500

@app.route('/dashboard')
def serve_dashboard():
    """Secure dashboard to view saved locations"""
    conn = sqlite3.connect(DB_PATH)
    # Configure to return dictionaries instead of tuples
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    # Get all records ordered by newest first
    cursor.execute('SELECT * FROM location_data ORDER BY timestamp DESC')
    records = cursor.fetchall()
    conn.close()
    
    # Pass the records to a template
    return render_template('dashboard.html', records=records)

if __name__ == '__main__':
    # Start the Flask server on port 5000
    print("\n" + "="*50)
    print("🚀 LOCATION TRACKER BACKEND STARTED 🚀")
    print("Dashboard available at: http://127.0.0.1:5000/dashboard")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
