from flask import Flask, render_template, jsonify, request
import os
import subprocess
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Ensure required environment variables are set
required_env_vars = ['LINKEDIN_EMAIL', 'LINKEDIN_PASSWORD']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-analysis', methods=['POST'])
def run_analysis():
    try:
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Run the scraper
        subprocess.run(['python', 'src/scraper.py'], check=True)
        
        # Run the analyzer
        subprocess.run(['python', 'src/analyzer.py'], check=True)
        
        # Run the suggestions generator
        subprocess.run(['python', 'src/suggestions.py'], check=True)
        
        # Get the latest analysis results
        data_dir = 'data'
        analysis_files = [f for f in os.listdir(data_dir) if f.startswith('analysis_insights_')]
        if not analysis_files:
            raise Exception("No analysis results found")
            
        latest_analysis = max(analysis_files)
        
        with open(os.path.join(data_dir, latest_analysis), 'r') as f:
            analysis_data = json.load(f)
            
        return jsonify({
            'success': True,
            'data': analysis_data
        })
    except Exception as e:
        app.logger.error(f"Analysis failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Use environment variable for port, default to 5000
    port = int(os.getenv('PORT', 5000))
    # Only enable debug mode in development
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug) 