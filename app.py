from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json
from scraper import CourtScraper
import os

app = Flask(__name__)
CORS(app)

# Database setup
def init_db():
    conn = sqlite3.connect('court_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS queries
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  case_type TEXT,
                  case_number TEXT,
                  year TEXT,
                  court_type TEXT,
                  court_name TEXT,
                  query_time TIMESTAMP,
                  raw_response TEXT,
                  parsed_data TEXT,
                  status TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS judgments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  query_id INTEGER,
                  filename TEXT,
                  file_path TEXT,
                  download_time TIMESTAMP,
                  FOREIGN KEY(query_id) REFERENCES queries(id))''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/fetch-case', methods=['POST'])
def fetch_case():
    try:
        data = request.json
        case_type = data.get('case_type')
        case_number = data.get('case_number')
        year = data.get('year')
        court_type = data.get('court_type', 'high_court')
        court_name = data.get('court_name', 'Delhi')
        
        if not all([case_type, case_number, year]):
            return jsonify({'error': 'Missing required fields', 'status': 'error'}), 400
        
        scraper = CourtScraper()
        result = scraper.fetch_case_details(
            case_type=case_type,
            case_number=case_number,
            year=year,
            court_type=court_type,
            court_name=court_name
        )
        
        if result.get('status') == 'error':
            return jsonify(result), 400
        
        # Store in database
        conn = sqlite3.connect('court_data.db')
        c = conn.cursor()
        c.execute('''INSERT INTO queries 
                     (case_type, case_number, year, court_type, court_name, 
                      query_time, raw_response, parsed_data, status)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (case_type, case_number, year, court_type, court_name,
                   datetime.now(), json.dumps(result.get('raw_html', '')),
                   json.dumps(result.get('parsed_data', {})), 'success'))
        query_id = c.lastrowid
        conn.commit()
        conn.close()
        
        result['query_id'] = query_id
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in fetch_case: {str(e)}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/download-judgment', methods=['POST'])
def download_judgment():
    try:
        data = request.json
        query_id = data.get('query_id')
        judgment_url = data.get('judgment_url')
        
        if not judgment_url:
            return jsonify({'error': 'No judgment URL provided', 'status': 'error'}), 400
        
        scraper = CourtScraper()
        file_path = scraper.download_judgment(judgment_url, query_id)
        
        if file_path and os.path.exists(file_path):
            conn = sqlite3.connect('court_data.db')
            c = conn.cursor()
            c.execute('''INSERT INTO judgments 
                         (query_id, filename, file_path, download_time)
                         VALUES (?, ?, ?, ?)''',
                      (query_id, os.path.basename(file_path), 
                       file_path, datetime.now()))
            conn.commit()
            conn.close()
            
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'Failed to download judgment', 'status': 'error'}), 500
            
    except Exception as e:
        print(f"Error in download_judgment: {str(e)}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/fetch-causelist', methods=['POST'])
def fetch_causelist():
    try:
        data = request.json
        court_type = data.get('court_type', 'high_court')
        court_name = data.get('court_name', 'Delhi')
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        print(f"Fetching causelist: {court_type}, {court_name}, {date}")  # Debug
        
        scraper = CourtScraper()
        result = scraper.fetch_causelist(court_type, court_name, date)
        
        # Ensure result is valid
        if result is None:
            result = {
                'status': 'error',
                'message': 'No data returned from scraper',
                'cases': []
            }
        
        if 'status' not in result:
            result['status'] = 'error'
        if 'cases' not in result:
            result['cases'] = []
        
        print(f"Causelist result: {result}")  # Debug
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in fetch_causelist: {str(e)}")
        return jsonify({'error': str(e), 'status': 'error', 'cases': []}), 500

@app.route('/api/courts')
def get_courts():
    """Return list of available courts"""
    courts = {
        'high_courts': [
            'Delhi', 'Mumbai', 'Kolkata', 'Chennai', 'Allahabad',
            'Karnataka', 'Gujarat', 'Rajasthan', 'Madhya Pradesh',
            'Kerala', 'Punjab and Haryana', 'Patna', 'Telangana'
        ],
        'district_courts': [
            'Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata'
        ]
    }
    return jsonify(courts)

@app.route('/api/history')
def get_history():
    """Get query history"""
    try:
        conn = sqlite3.connect('court_data.db')
        c = conn.cursor()
        c.execute('''SELECT id, case_type, case_number, year, court_name, 
                            query_time, status 
                     FROM queries 
                     ORDER BY query_time DESC LIMIT 50''')
        rows = c.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'case_type': row[1],
                'case_number': row[2],
                'year': row[3],
                'court_name': row[4],
                'query_time': row[5],
                'status': row[6]
            })
        
        return jsonify(history)
    except Exception as e:
        print(f"Error in get_history: {str(e)}")
        return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)