**AI Project Risk Assessment Tool for Kenyan Public Sector**<br>

 **Research Overview**<br>

Research Title: Predicting Public Sector AI Project Failure in Kenya: A Machine Learning–Driven Risk Assessment and Mitigation Framework

This tool implements a quantitative data collection system for researching AI project failure risks in Kenya's public sector. It collects structured risk factor data to support machine learning model development for failure prediction.

 **Research Objectives Addressed**
- Analysis Objective: Identify context-specific risk factors through systematic data collection

- Modeling Objective: Gather training data for ML models predicting AI project failure probability

- Framework Development: Enable data-driven risk assessment and mitigation strategies

- Validation Objective: Provide baseline data for comparative analysis with traditional methods

 **System Architecture**

graph TB
    subgraph "Client Tier (Frontend)"
        UI["<b>User Interface</b><br/>Browser-based Application<br/>• HTML5/CSS3/JavaScript<br/>• React/Vue.js Components<br/>• Real-time Validation<br/>• Accessibility Features<br/>• LocalStorage Fallback"]
    end
    
    subgraph "Application Tier (Backend)"
        API["<b>API Gateway & Business Logic</b><br/>• Python Flask/Node.js Express<br/>• RESTful Endpoints<br/>• Data Validation<br/>• Authentication/Authorization<br/>• Rate Limiting"]
    end
    
    subgraph "Data Tier (Storage)"
        DB1["<b>PostgreSQL</b><br/>• Structured Data<br/>• ACID Compliance<br/>• Relational Schema"]
        DB2["<b>MongoDB</b><br/>• Unstructured Data<br/>• JSON Documents<br/>• Flexible Schema"]
        DB3["<b>Redis</b><br/>• Caching Layer<br/>• Session Management<br/>• Real-time Analytics"]
    end
    
    UI -- "HTTPS/JSON API Calls<br/>Port: 3000" --> API
    API -- "Database Operations<br/>Connection Pooling" --> DB1
    API -- "Document Operations<br/>Flexible Queries" --> DB2
    API -- "Cache Operations<br/>Pub/Sub Messaging" --> DB3
    
    style UI fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style API fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style DB1 fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    style DB2 fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style DB3 fill:#fce4ec,stroke:#880e4f,stroke-width:2px

**Key Components**

Component	Technology	Purpose
Frontend Interface	HTML5, CSS3, JavaScript	Data collection, validation, user interaction
Backend Server	Python HTTP Server (zero-dependency)	API endpoints, data persistence
Data Storage	SQLite + JSON files	Structured and raw data storage
Export Format	CSV/JSON	Research data sharing and analysis

 **Quantitative Data Collected**

**1. Project Information**
- Sector: Health, Education, Agriculture, Transport, Finance, Security

- Budget: KES millions (continuous, ratio scale)

- Duration: Months (discrete, ratio scale)

**2. Risk Factors (Likert Scale 1-5)**

Category	Specific Factors	Measurement Rationale
Technical	Data Quality, Technical Expertise	System capability and implementation readiness
Organizational	Stakeholder Support, Budget Stability	Institutional commitment and resource allocation
Contextual	Infrastructure Reliability, Regulatory Compliance	Kenya-specific implementation challenges

**3. Outcome Metrics**

Project Status: Planning, Implementation, Completed, Failed

Success Score: 0-10 scale (ordinal)

Failure Reason: Technical, Budget, Stakeholder, Data, Infrastructure

 **Implementation Details**

Frontend Features
Responsive Design: Mobile-first CSS with media queries

Real-time Validation: Client-side form validation

Offline Capability: LocalStorage fallback

Data Export: CSV generation for research analysis

Accessibility: WCAG 2.1 AA compliant design

Backend Capabilities
Zero Dependencies: Uses only Python standard library

RESTful API: JSON-based communication

CORS Enabled: Cross-origin resource sharing

Data Persistence: SQLite database with JSON backups

Research Analytics: Built-in statistical functions

**Getting Started**

Quick Start (Frontend Only - No Installation)
Open frontend/index.html in any modern web browser

Complete the consent form

Fill in the risk assessment

Submit data (saved to browser storage)

Export CSV for analysis

Full Setup (With Backend)
Option A: Minimal Server (Recommended)
bash
cd backend
python minimal_server.py
Uses only Python standard library - no installations needed

Option B: Flask Server (Advanced)
bash
cd backend
pip install -r requirements.txt
python server.py
Server Endpoints
POST /api/submit - Submit risk assessment data

GET /api/stats - Get research statistics

GET /api/export - Export data as CSV

GET /api/health - Server health check

**📁 Project Structure**

text
AI-PROJECT-RISK-TOOL/
├── README.md                    # This file
├── frontend/                    # User interface
│   ├── index.html              # Main application
│   ├── style.css               # Styling
│   └── script.js               # Application logic
└── backend/                    # Server implementation
    ├── minimal_server.py       # Zero-dependency server
    ├── server.py               # Flask server (alternative)
    ├── app_simple.py           # Simple data collector
    ├── requirements.txt        # Python dependencies
    └── data/                   # Generated data storage
        ├── assessments.db      # SQLite database
        ├── assessments.json    # JSON backup
        └── *.csv               # Export files

**Ethical Considerations**

Privacy Protection

Pseudonymization: Session-based identifiers only

Data Minimization: Collects only research-essential data

Local Processing: Client-side data handling when possible

Explicit Consent: Multi-tiered consent system

Research Ethics Compliance

Informed Consent: Clear explanation of research purpose

Voluntary Participation: No coercion, right to withdraw

Data Security: Local storage with option for server backup

Transparency: Open-source tool with documented methodology

 **Data Quality Assurance**

Validation Rules

Range Validation: Numerical bounds (e.g., budget > 0)

Completeness: Required fields enforcement

Consistency: Logical relationship checks

Type Safety: Data type verification

Quality Metrics
Completeness: >95% required fields populated

Accuracy: <5% data entry errors

Timeliness: Real-time submission tracking

**Research Applications**

This tool supports the following research activities:

- Risk Factor Analysis: Identifying key failure predictors in Kenyan context

- ML Model Training: Providing labeled data for predictive algorithms

- Framework Validation: Testing risk assessment methodologies

- Comparative Studies: Benchmarking against traditional approaches

**License**
This tool is developed for academic research purposes. Code is available for modification and extension with attribution.