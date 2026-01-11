# app.py
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from trip_planner import TripPlanner
from pdf_generator import generate_pdf
from config import Config
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.secret_key = Config.SECRET_KEY

# Initialize trip planner
planner = TripPlanner()

# Ensure directories exist
Config.ensure_directories()

@app.route('/')
def home():
    """Home page"""
    return render_template('index.html')

@app.route('/plan', methods=['POST'])
def create_plan():
    """Create trip plan"""
    try:
        data = request.json
        
        # Validate
        if not data:
            return jsonify({'success': False, 'error': 'No data'})
        
        required = ['origin', 'destination', 'departure_date']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing: {field}'})
        
        print(f"\n📋 Planning trip: {data['origin']} → {data['destination']}")
        
        # Create plan
        trip_plan = planner.create_trip_plan(data)
        
        # Generate PDF
        pdf_filename = generate_pdf(trip_plan)
        
        # Check if using sample data
        using_sample = False
        if trip_plan.get('flights'):
            using_sample = trip_plan['flights'][0].get('is_sample', False)
        
        return jsonify({
            'success': True,
            'plan': trip_plan,
            'pdf_url': f'/download/{pdf_filename}',
            'using_sample': using_sample
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<filename>')
def download_pdf(filename):
    """Download PDF"""
    try:
        return send_from_directory(
            Config.PDF_OUTPUT_DIR,
            filename,
            as_attachment=True,
            download_name=f"trip_plan_{filename.split('_')[-1]}"
        )
    except:
        return jsonify({'error': 'File not found'}), 404

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'amadeus_configured': bool(Config.AMADEUS_API_KEY and Config.AMADEUS_API_SECRET)
    })

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Trip Planner Assistant")
    print("="*50)
    print(f"🔑 Amadeus API: {'Configured' if Config.validate() else 'Not configured (using sample data)'}")
    print("🌐 Web Interface: http://127.0.0.1:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)