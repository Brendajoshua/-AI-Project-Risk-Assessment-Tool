// Data Model for AI Project Risk Assessment
let projectData = {
    consentGiven: false,
    timestamp: '',
    sessionId: '',
    
    // Project Information
    projectInfo: {
        sector: '',
        budget: '',
        duration: '',
        teamSize: ''
    },
    
    // Risk Factors (1-5 scale)
    riskFactors: {
        data_quality: 0,
        tech_expertise: 0,
        stakeholder: 0,
        budget_stability: 0,
        infrastructure: 0,
        regulatory: 0,
        data_privacy: 0,
        change_management: 0
    },
    
    // Project Outcome
    outcome: {
        status: '',
        successScore: 5,
        failureReason: 'none',
        completionDate: '',
        lessonsLearned: ''
    },
    
    // Metadata
    metadata: {
        submissionTime: '',
        userAgent: navigator.userAgent,
        screenResolution: `${window.screen.width}x${window.screen.height}`
    }
};

// Initialize session
function initSession() {
    projectData.sessionId = 'ai_risk_' + Math.random().toString(36).substr(2, 9);
    projectData.timestamp = new Date().toISOString();
    updatePreview();
}

// Start assessment after consent
function startAssessment() {
    const checkbox = document.getElementById('consentCheckbox');
    const consentSection = document.getElementById('consentSection');
    const assessmentSection = document.getElementById('assessmentSection');
    
    if (checkbox.checked) {
        projectData.consentGiven = true;
        consentSection.classList.add('hidden');
        assessmentSection.classList.remove('hidden');
        initSession();
        showStatus('Consent recorded. Please complete the risk assessment.', 'success');
    } else {
        showStatus('Please agree to the consent terms to continue.', 'warning');
    }
}

// Set risk factor values
function setRisk(factor, value) {
    // Update data model
    projectData.riskFactors[factor] = value;
    
    // Update UI - remove selected class from all buttons in this group
    const buttons = document.querySelectorAll(`[onclick*="${factor}"]`);
    buttons.forEach(btn => btn.classList.remove('selected'));
    
    // Add selected class to clicked button
    event.target.classList.add('selected');
    
    // Update value display
    document.getElementById(`${factor}_val`).textContent = value;
    
    updatePreview();
}

// Update form data
function updateFormData() {
    // Project info
    projectData.projectInfo.sector = document.getElementById('projectSector').value;
    projectData.projectInfo.budget = document.getElementById('projectBudget').value;
    projectData.projectInfo.duration = document.getElementById('projectDuration').value;
    
    // Outcome
    projectData.outcome.status = document.getElementById('projectStatus').value;
    projectData.outcome.successScore = parseInt(document.getElementById('successScore').value);
    projectData.outcome.failureReason = document.getElementById('failureReason').value;
    
    // Update score display
    document.getElementById('scoreValue').textContent = projectData.outcome.successScore;
    
    updatePreview();
}

// Update preview display
function updatePreview() {
    const preview = document.getElementById('dataPreview');
    
    // Calculate risk score
    const riskValues = Object.values(projectData.riskFactors).filter(v => v > 0);
    const avgRisk = riskValues.length > 0 ? 
        (riskValues.reduce((a, b) => a + b, 0) / riskValues.length).toFixed(2) : 'N/A';
    
    // Create formatted preview
    const previewData = {
        'Session ID': projectData.sessionId,
        'Sector': projectData.projectInfo.sector || 'Not set',
        'Budget (KES M)': projectData.projectInfo.budget || 'Not set',
        'Average Risk Score': avgRisk,
        'Project Status': projectData.outcome.status || 'Not set',
        'Success Score': projectData.outcome.successScore,
        'Data Points Collected': Object.keys(projectData.riskFactors).filter(k => projectData.riskFactors[k] > 0).length + '/8'
    };
    
    preview.textContent = JSON.stringify(previewData, null, 2);
}

// Validate assessment data
function validateAssessment() {
    const errors = [];
    
    // Check consent
    if (!projectData.consentGiven) {
        errors.push('Consent not given');
    }
    
    // Check project info
    if (!projectData.projectInfo.sector) {
        errors.push('Project sector is required');
    }
    
    if (!projectData.projectInfo.budget || projectData.projectInfo.budget <= 0) {
        errors.push('Valid budget amount is required');
    }
    
    // Check risk factors (at least 3 should be rated)
    const ratedRisks = Object.values(projectData.riskFactors).filter(v => v > 0).length;
    if (ratedRisks < 3) {
        errors.push('Please rate at least 3 risk factors');
    }
    
    return errors;
}

// Submit assessment
async function submitAssessment() {
    // Update form data
    updateFormData();
    
    // Validate
    const errors = validateAssessment();
    if (errors.length > 0) {
        showStatus('Validation errors: ' + errors.join(', '), 'error');
        return;
    }
    
    // Add submission timestamp
    projectData.metadata.submissionTime = new Date().toISOString();
    
    // Calculate derived metrics
    projectData.metadata.totalRiskScore = calculateTotalRisk();
    projectData.metadata.riskCategory = categorizeRisk();
    
    try {
        // Try to send to backend
        const response = await fetch('http://localhost:5000/api/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(projectData)
        });
        
        if (response.ok) {
            // Also store locally as backup
            storeLocally();
            showStatus('✅ Assessment submitted successfully! Thank you for your contribution.', 'success');
            resetForm();
        } else {
            throw new Error('Server error');
        }
    } catch (error) {
        // Fallback to local storage
        storeLocally();
        showStatus('📱 Data saved locally (offline mode). Connect to internet to sync.', 'warning');
    }
}

// Calculate total risk score
function calculateTotalRisk() {
    const values = Object.values(projectData.riskFactors).filter(v => v > 0);
    if (values.length === 0) return 0;
    
    const sum = values.reduce((a, b) => a + b, 0);
    const maxPossible = values.length * 5;
    
    return Math.round((sum / maxPossible) * 100);
}

// Categorize risk level
function categorizeRisk() {
    const score = calculateTotalRisk();
    
    if (score < 30) return 'Low Risk';
    if (score < 60) return 'Medium Risk';
    if (score < 80) return 'High Risk';
    return 'Critical Risk';
}

// Store data locally
function storeLocally() {
    const submissions = JSON.parse(localStorage.getItem('aiRiskAssessments') || '[]');
    submissions.push(projectData);
    localStorage.setItem('aiRiskAssessments', JSON.stringify(submissions));
    
    console.log(`Stored locally. Total submissions: ${submissions.length}`);
}

// Export data
function exportData() {
    const submissions = JSON.parse(localStorage.getItem('aiRiskAssessments') || '[]');
    
    if (submissions.length === 0) {
        showStatus('No data to export. Please submit an assessment first.', 'warning');
        return;
    }
    
    // Export as CSV
    const headers = ['Session ID', 'Sector', 'Budget', 'Duration', 'Avg Risk', 'Status', 'Success Score', 'Risk Category'];
    
    const csvRows = [];
    csvRows.push(headers.join(','));
    
    submissions.forEach(sub => {
        const riskValues = Object.values(sub.riskFactors).filter(v => v > 0);
        const avgRisk = riskValues.length > 0 ? 
            (riskValues.reduce((a, b) => a + b, 0) / riskValues.length).toFixed(2) : 'N/A';
        
        const row = [
            sub.sessionId,
            sub.projectInfo.sector,
            sub.projectInfo.budget,
            sub.projectInfo.duration,
            avgRisk,
            sub.outcome.status,
            sub.outcome.successScore,
            sub.metadata.riskCategory || 'Not calculated'
        ];
        csvRows.push(row.join(','));
    });
    
    const csvContent = csvRows.join('\n');
    
    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai_risk_data_${new Date().toISOString().slice(0,10)}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    showStatus(`📥 Exported ${submissions.length} assessments to CSV`, 'success');
}

// Reset form
function resetForm() {
    // Reset form fields
    document.getElementById('projectSector').value = '';
    document.getElementById('projectBudget').value = '';
    document.getElementById('projectDuration').value = '';
    document.getElementById('projectStatus').value = 'planning';
    document.getElementById('successScore').value = 5;
    document.getElementById('failureReason').value = 'none';
    
    // Reset risk buttons
    document.querySelectorAll('.scale-buttons button').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // Reset risk value displays
    document.querySelectorAll('.risk-value').forEach(span => {
        span.textContent = 'Not set';
    });
    
    // Reset data model (keep consent and session)
    projectData.projectInfo = { sector: '', budget: '', duration: '', teamSize: '' };
    projectData.riskFactors = Object.keys(projectData.riskFactors).reduce((acc, key) => {
        acc[key] = 0;
        return acc;
    }, {});
    projectData.outcome = { status: '', successScore: 5, failureReason: 'none', completionDate: '', lessonsLearned: '' };
    projectData.timestamp = new Date().toISOString();
    
    updatePreview();
    showStatus('Form reset. You can start a new assessment.', 'success');
}

// Show status messages
function showStatus(message, type = 'success') {
    const statusDiv = document.getElementById('statusMessage');
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type}`;
    statusDiv.classList.remove('hidden');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        statusDiv.classList.add('hidden');
    }, 5000);
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Update form data on input change
    document.getElementById('projectSector').addEventListener('change', updateFormData);
    document.getElementById('projectBudget').addEventListener('input', updateFormData);
    document.getElementById('projectDuration').addEventListener('input', updateFormData);
    document.getElementById('projectStatus').addEventListener('change', updateFormData);
    document.getElementById('successScore').addEventListener('input', updateFormData);
    document.getElementById('failureReason').addEventListener('change', updateFormData);
    
    // Update score display for range slider
    document.getElementById('successScore').addEventListener('input', function() {
        document.getElementById('scoreValue').textContent = this.value;
    });
    
    // Check for existing data
    const submissions = JSON.parse(localStorage.getItem('aiRiskAssessments') || '[]');
    if (submissions.length > 0) {
        showStatus(`Welcome back! You have ${submissions.length} previous assessments.`, 'success');
    }
    
    // Initial preview
    updatePreview();
});