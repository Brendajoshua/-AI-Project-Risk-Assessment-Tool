from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import csv
import sqlite3
import pandas as pd
from datetime import datetime
import hashlib
import os
import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Create data directory
os.makedirs('data', exist_ok=True)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('data/projects.db')
    cursor = conn.cursor()
    
    # Projects table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        sector TEXT NOT NULL,
        budget REAL,
        duration_months INTEGER,
        submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        consent_given BOOLEAN DEFAULT FALSE,
        risk_score REAL,
        success_score INTEGER,
        status TEXT,
        failure_reason TEXT
    )
    ''')
    
    # Risk factors table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS risk_factors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        factor_name TEXT NOT NULL,
        risk_value INTEGER CHECK(risk_value BETWEEN 1 AND 5),
        FOREIGN KEY (session_id) REFERENCES projects (session_id)
    )
    ''')
    
    # Research metadata table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS research_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        data_type TEXT,
        collection_method TEXT,
        research_phase TEXT,
        validation_status TEXT DEFAULT 'pending',
        FOREIGN KEY (session_id) REFERENCES projects (session_id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Helper function for data anonymization
def anonymize_data(data):
    """Pseudonymize sensitive data for research purposes"""
    anonymized = data.copy()
    
    # Hash session ID for additional privacy
    if 'sessionId' in anonymized:
        anonymized['hashed_id'] = hashlib.sha256(
            anonymized['sessionId'].encode()
        ).hexdigest()[:16]
    
    # Remove any potential personal identifiers
    fields_to_remove = ['userAgent', 'screenResolution', 'ip_address']
    for field in fields_to_remove:
        if field in anonymized.get('metadata', {}):
            del anonymized['metadata'][field]
    
    return anonymized

# Calculate derived metrics
def calculate_metrics(risk_factors):
    """Calculate risk metrics from factor scores"""
    if not risk_factors:
        return {
            'total_risk': 0,
            'risk_level': 'Unknown',
            'critical_factors': []
        }
    
    values = [v for v in risk_factors.values() if v > 0]
    avg_risk = sum(values) / len(values) if values else 0
    
    # Determine risk level
    if avg_risk < 2.0:
        risk_level = 'Low'
    elif avg_risk < 3.5:
        risk_level = 'Medium'
    elif avg_risk < 4.5:
        risk_level = 'High'
    else:
        risk_level = 'Critical'
    
    # Identify critical factors (score >= 4)
    critical_factors = [
        factor for factor, score in risk_factors.items()
        if score >= 4
    ]
    
    return {
        'total_risk': round(avg_risk, 2),
        'risk_level': risk_level,
        'critical_factors': critical_factors,
        'factor_count': len(values)
    }

# API Endpoints
@app.route('/')
def index():
    """Home endpoint"""
    return jsonify({
        'service': 'AI Project Risk Assessment API',
        'version': '1.0',
        'research_topic': 'Predicting Public Sector AI Project Failure in Kenya',
        'endpoints': {
            'POST /api/submit': 'Submit risk assessment',
            'GET /api/data': 'Get all assessments',
            'GET /api/export/csv': 'Export data as CSV',
            'GET /api/stats': 'Get research statistics',
            'GET /api/health': 'Health check'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if os.path.exists('data/projects.db') else 'not_found'
    })

@app.route('/api/submit', methods=['POST'])
def submit_assessment():
    """Submit a risk assessment"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['sessionId', 'projectInfo', 'riskFactors', 'consentGiven']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check consent
        if not data['consentGiven']:
            return jsonify({'error': 'Consent not given'}), 403
        
        # Anonymize data for research
        anonymized_data = anonymize_data(data)
        
        # Calculate risk metrics
        risk_metrics = calculate_metrics(data['riskFactors'])
        
        # Connect to database
        conn = sqlite3.connect('data/projects.db')
        cursor = conn.cursor()
        
        # Insert project data
        cursor.execute('''
        INSERT INTO projects 
        (session_id, sector, budget, duration_months, consent_given, 
         risk_score, success_score, status, failure_reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['sessionId'],
            data['projectInfo'].get('sector', 'Unknown'),
            float(data['projectInfo'].get('budget', 0)),
            int(data['projectInfo'].get('duration', 0)),
            True,  # consent_given
            risk_metrics['total_risk'],
            data['outcome'].get('successScore', 5),
            data['outcome'].get('status', 'unknown'),
            data['outcome'].get('failureReason', 'none')
        ))
        
        # Insert risk factors
        for factor, value in data['riskFactors'].items():
            if value > 0:  # Only insert rated factors
                cursor.execute('''
                INSERT INTO risk_factors (session_id, factor_name, risk_value)
                VALUES (?, ?, ?)
                ''', (data['sessionId'], factor, value))
        
        # Insert research metadata
        cursor.execute('''
        INSERT INTO research_metadata (session_id, data_type, collection_method, research_phase)
        VALUES (?, ?, ?, ?)
        ''', (
            data['sessionId'],
            'quantitative_risk_assessment',
            'web_tool',
            'data_collection'
        ))
        
        conn.commit()
        conn.close()
        
        # Save JSON backup
        json_filename = f"data/assessment_{data['sessionId']}.json"
        with open(json_filename, 'w') as f:
            json.dump(anonymized_data, f, indent=2)
        
        print(f"✅ Assessment saved: {data['sessionId']}")
        
        return jsonify({
            'success': True,
            'message': 'Risk assessment submitted successfully',
            'session_id': data['sessionId'],
            'risk_analysis': risk_metrics,
            'data_use': 'This data will be used for machine learning model training and risk framework validation',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data', methods=['GET'])
def get_all_data():
    """Get all assessment data"""
    try:
        conn = sqlite3.connect('data/projects.db')
        
        # Get projects with their risk factors
        query = '''
        SELECT 
            p.session_id,
            p.sector,
            p.budget,
            p.duration_months,
            p.risk_score,
            p.success_score,
            p.status,
            p.failure_reason,
            p.submission_date,
            GROUP_CONCAT(rf.factor_name || ':' || rf.risk_value) as risk_factors
        FROM projects p
        LEFT JOIN risk_factors rf ON p.session_id = rf.session_id
        WHERE p.consent_given = TRUE
        GROUP BY p.session_id
        ORDER BY p.submission_date DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Convert to dictionary
        data = df.to_dict('records')
        
        return jsonify({
            'success': True,
            'count': len(data),
            'data': data,
            'research_applications': [
                'Training ML models for failure prediction',
                'Identifying key risk factors in Kenyan context',
                'Validating risk mitigation framework',
                'Comparative analysis with traditional methods'
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export data as CSV for research analysis"""
    try:
        conn = sqlite3.connect('data/projects.db')
        
        # Complex query for research analysis
        query = '''
        SELECT 
            p.session_id,
            p.sector,
            p.budget,
            p.duration_months,
            p.risk_score,
            p.success_score,
            p.status,
            p.failure_reason,
            COUNT(rf.id) as factors_rated,
            AVG(rf.risk_value) as avg_factor_score,
            SUM(CASE WHEN rf.risk_value >= 4 THEN 1 ELSE 0 END) as critical_factors,
            p.submission_date
        FROM projects p
        LEFT JOIN risk_factors rf ON p.session_id = rf.session_id
        WHERE p.consent_given = TRUE
        GROUP BY p.session_id
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return jsonify({'error': 'No data available for export'}), 404
        
        # Create CSV file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/ai_risk_research_{timestamp}.csv"
        
        df.to_csv(filename, index=False)
        
        return send_file(
            filename,
            as_attachment=True,
            download_name=f"kenya_ai_risk_data_{timestamp}.csv",
            mimetype='text/csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/json', methods=['GET'])
def export_json():
    """Export data as JSON for ML model training"""
    try:
        conn = sqlite3.connect('data/projects.db')
        
        # Get data in ML-ready format
        projects_query = '''
        SELECT * FROM projects WHERE consent_given = TRUE
        '''
        factors_query = '''
        SELECT session_id, factor_name, risk_value FROM risk_factors
        '''
        
        projects_df = pd.read_sql_query(projects_query, conn)
        factors_df = pd.read_sql_query(factors_query, conn)
        conn.close()
        
        # Transform to nested JSON structure
        data = []
        for _, project in projects_df.iterrows():
            project_data = project.to_dict()
            
            # Add risk factors as nested array
            session_factors = factors_df[factors_df['session_id'] == project['session_id']]
            project_data['risk_factors'] = session_factors.to_dict('records')
            
            data.append(project_data)
        
        # Save JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/ml_training_data_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return send_file(
            filename,
            as_attachment=True,
            download_name=f"ml_training_data_{timestamp}.json",
            mimetype='application/json'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get research statistics"""
    try:
        conn = sqlite3.connect('data/projects.db')
        
        # Basic counts
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM projects WHERE consent_given = TRUE')
        total_assessments = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT sector) FROM projects')
        sectors_covered = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(risk_score) FROM projects')
        avg_risk_score = cursor.fetchone()[0]
        
        cursor.execute('''
        SELECT status, COUNT(*) as count 
        FROM projects 
        WHERE consent_given = TRUE 
        GROUP BY status
        ''')
        status_counts = dict(cursor.fetchall())
        
        cursor.execute('''
        SELECT factor_name, AVG(risk_value) as avg_score, COUNT(*) as count
        FROM risk_factors
        GROUP BY factor_name
        ORDER BY avg_score DESC
        LIMIT 5
        ''')
        top_risks = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'research_statistics': {
                'total_assessments': total_assessments,
                'sectors_covered': sectors_covered,
                'average_risk_score': round(avg_risk_score, 2) if avg_risk_score else 0,
                'project_status_distribution': status_counts,
                'top_risk_factors': [
                    {'factor': factor, 'average_score': round(score, 2), 'occurrences': count}
                    for factor, score, count in top_risks
                ],
                'data_collection_period': {
                    'started': '2024-01-01',  # Would be dynamic in production
                    'current': datetime.now().strftime('%Y-%m-%d')
                }
            },
            'research_progress': {
                'phase': 'Data Collection',
                'next_phase': 'Model Training',
                'data_sufficiency': 'Sufficient for preliminary analysis' if total_assessments >= 50 else 'Collecting more data'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/questions', methods=['GET'])
def get_research_questions():
    """Display research questions addressed by this tool"""
    return jsonify({
        'research_topic': 'Predicting Public Sector AI Project Failure in Kenya',
        'research_questions_addressed': [
            {
                'question': 'What are the primary contextual factors contributing to AI project failures in Kenya\'s public sector?',
                'data_collected': 'Sector-specific risks, infrastructure reliability, regulatory compliance'
            },
            {
                'question': 'How can machine learning techniques be adapted to predict AI project failure in resource-constrained environments?',
                'data_collected': 'Quantitative risk factors, project outcomes, success/failure patterns'
            },
            {
                'question': 'What components should constitute an effective risk mitigation framework?',
                'data_collected': 'Risk factor weights, critical failure points, intervention effectiveness'
            },
            {
                'question': 'How does a predictive, data-driven approach compare to traditional methods?',
                'data_collected': 'Baseline data for comparative analysis, accuracy metrics, practical utility measures'
            }
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting AI Project Risk Assessment Backend...")
    print("📊 Research Tool for: Predicting Public Sector AI Project Failure in Kenya")
    print("🔗 API running at: http://localhost:5000")
    print("📁 Data storage: SQLite database at data/projects.db")
    print("\n🌐 Frontend should be opened separately (open frontend/index.html)")
    app.run(debug=True, port=5000)