import os
import sqlite3
from flask import Flask, render_template, request, jsonify, send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

app = Flask(__name__)
DB_NAME = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_tier(score):
    if score >= 26:
        return "Tier 1 (Critical)"
    elif score >= 20:
        return "Tier 2 (High)"
    elif score >= 14:
        return "Tier 3 (Medium)"
    elif score >= 8:
        return "Tier 4 (Low)"
    else:
        return "Tier 5 (Informational)"

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            data_class TEXT,
            impact INTEGER NOT NULL,
            likelihood INTEGER NOT NULL,
            rto INTEGER NOT NULL,
            exposure INTEGER NOT NULL,
            score INTEGER NOT NULL,
            tier TEXT NOT NULL,
            justification TEXT
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM assets')
    count = cursor.fetchone()[0]
    if count == 0:
        sample_assets = [
            ("Active Directory / IDP", "Identity & Access", "Enterprise Identity Management & Kerberos/LDAP", "Credentials, Logs", 5, 4, 5, 4, 28, "Tier 1 (Critical)", "Core identity provider handling all user auth."),
            ("Edge Firewalls & Gateways", "Network Infrastructure", "Perimeter BGP routers and Next-Gen Firewalls", "Network Traffic, Routing", 5, 3, 5, 5, 28, "Tier 1 (Critical)", "Primary barrier facing public internet threats."),
            ("Core Production DB", "Enterprise Operations", "Main customer ledger and transactional engine", "PII, Financial Records", 5, 3, 4, 2, 23, "Tier 2 (High)", "Holds critical customer account records."),
            ("Email & Internal Messaging", "Collaboration", "Corporate communication relay and mail servers", "Emails, Comms, Files", 3, 4, 3, 3, 19, "Tier 3 (Medium)", "Internal staff sync channels."),
            ("Customer Relationship Mgmt (CRM)", "Sales & Support", "Client database and ticket tracking backend", "Client Contacts, Deals", 3, 3, 3, 3, 18, "Tier 3 (Medium)", "Handles sales pipeline and customer support tickets."),
            ("Internal Workstations", "End-User Computing", "Local Data, User Cache", "Endpoints, Files", 2, 4, 4, 2, 16, "Tier 4 (Low)", "Standard corporate developer laptops and workstations."),
            ("Development & Staging", "R&D Sandbox", "Source Code, Test Data", "Code, Test Data", 2, 3, 1, 1, 11, "Tier 4 (Low)", "Isolated development environment with mock data."),
            ("Guest Wi-Fi Network", "Facility Services", "Unauthenticated Traffic", "Facility Services", 1, 2, 1, 1, 7, "Tier 5 (Informational)", "Isolated visitor internet access segment.")
        ]
        
        for name, cat, desc, dclass, imp, lik, rto, exp, score, tier, just in sample_assets:
            cursor.execute('''
                INSERT INTO assets (name, category, description, data_class, impact, likelihood, rto, exposure, score, tier, justification)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, cat, desc, dclass, imp, lik, rto, exp, score, tier, just))
            
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/operations')
def operations():
    return render_template('operations.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/assets', methods=['GET'])
def get_assets():
    conn = get_db_connection()
    assets = conn.execute('SELECT * FROM assets ORDER BY score DESC').fetchall()
    conn.close()
    return jsonify([dict(asset) for asset in assets])

@app.route('/api/assets', methods=['POST'])
def add_asset():
    data = request.json
    name = data.get('name')
    category = data.get('category')
    description = data.get('description', '')
    data_class = data.get('data_class', '')
    impact = int(data.get('impact', 3))
    likelihood = int(data.get('likelihood', 3))
    rto = int(data.get('rto', 3))
    exposure = int(data.get('exposure', 3))
    justification = data.get('justification', '')

    score = (impact * 2) + (likelihood * 1) + (rto * 2) + (exposure * 1)
    tier = calculate_tier(score)

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO assets (name, category, description, data_class, impact, likelihood, rto, exposure, score, tier, justification)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, category, description, data_class, impact, likelihood, rto, exposure, score, tier, justification))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "score": score, "tier": tier})

@app.route('/api/assets/<int:id>', methods=['DELETE'])
def delete_asset(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM assets WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/flush', methods=['POST'])
def flush_database():
    conn = get_db_connection()
    conn.execute('DELETE FROM assets')
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Database wiped clean."})

@app.route('/api/simulate', methods=['POST'])
def simulate_attack():
    data = request.json
    asset_id = data.get('asset_id')
    
    conn = get_db_connection()
    target = conn.execute('SELECT * FROM assets WHERE id = ?', (asset_id,)).fetchone()
    if not target:
        conn.close()
        return jsonify({"status": "error", "message": "Asset not found."}), 404
        
    all_assets = conn.execute('SELECT * FROM assets WHERE id != ?', (asset_id,)).fetchall()
    conn.close()
    
    affected_nodes = []
    target_name = target['name'].lower()
    
    for asset in all_assets:
        cat = asset['category'].lower()
        if 'firewall' in target_name or 'gateway' in target_name:
            if 'database' in asset['name'].lower() or 'identity' in asset['name'].lower() or 'infrastructure' in cat:
                affected_nodes.append(dict(asset))
        elif 'identity' in target_name or 'active directory' in target_name:
            affected_nodes.append(dict(asset))
        else:
            if asset['category'] == target['category'] or asset['exposure'] >= 3:
                affected_nodes.append(dict(asset))
                
    seen_ids = set()
    unique_affected = []
    for node in affected_nodes:
        if node['id'] not in seen_ids:
            seen_ids.add(node['id'])
            unique_affected.append(node)

    blast_score_sum = target['score'] + sum([node['score'] for node in unique_affected])
    
    return jsonify({
        "status": "success",
        "target": dict(target),
        "affected_count": len(unique_affected),
        "affected_nodes": unique_affected,
        "total_blast_score": blast_score_sum
    })

@app.route('/api/export/pdf', methods=['GET'])
def export_pdf():
    conn = get_db_connection()
    assets = conn.execute('SELECT * FROM assets ORDER BY score DESC').fetchall()
    conn.close()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#003366'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        spaceAfter=15
    )

    elements.append(Paragraph("RiskOptima // Executive Risk Report", title_style))
    elements.append(Paragraph("Generated via Tactical Criticality Engine (NIST SP 800-30 Standard)", subtitle_style))
    elements.append(Spacer(1, 10))

    table_data = [["Asset Name", "Category", "Data Class", "Score", "Tier"]]
    for a in assets:
        table_data.append([a['name'], a['category'], a['data_class'], str(a['score']), a['tier']])

    t = Table(table_data, colWidths=[150, 110, 110, 50, 135])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f9f9f9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
    ]))

    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name="RiskOptima_Executive_Risk_Report.pdf", mimetype='application/pdf')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part uploaded."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file."}), 400

    try:
        content = file.read().decode('utf-8')
        lines = content.splitlines()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        imported_count = 0
        for line in lines:
            if not line.strip() or line.startswith('name') or line.startswith('AssetName'):
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 8:
                name, cat, desc, dclass, imp, lik, rto, exp = parts[0], parts[1], parts[2], parts[3], int(parts[4]), int(parts[5]), int(parts[6]), int(parts[7])
                just = parts[8] if len(parts) > 8 else "Bulk Ingestion"
                
                score = (imp * 2) + (likelihood * 1) + (rto * 2) + (exposure * 1)
                tier = calculate_tier(score)
                
                cursor.execute('''
                    INSERT INTO assets (name, category, description, data_class, impact, likelihood, rto, exposure, score, tier, justification)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, cat, desc, dclass, imp, lik, rto, exp, score, tier, just))
                imported_count += 1
                
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": f"Successfully ingested {imported_count} records."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
