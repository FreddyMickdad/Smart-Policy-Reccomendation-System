
import sqlite3
from typing import List, Dict, Any
import json
import os

DB_FILE = "policies_v2.db"

SAMPLE_POLICIES = [
    {
        "name": "Family Health Protect",
        "coverage_type": "medical,life",
        "eligibility": "0-65",
        "premium_min": 5000,
        "premium_max": 15000,
        "description": "Comprehensive family medical cover with optional life add-on.",
        "risk_tolerance": "medium"
    },
    {
        "name": "MotorSecure Classic",
        "coverage_type": "motor",
        "eligibility": "18-75",
        "premium_min": 3000,
        "premium_max": 12000,
        "description": "Third-party + limited own damage for most private cars.",
        "risk_tolerance": "low"
    },
    {
        "name": "EduFuture Savings Plan",
        "coverage_type": "education,life",
        "eligibility": "18-60",
        "premium_min": 2000,
        "premium_max": 8000,
        "description": "Savings and education endowment plan for children's future.",
        "risk_tolerance": "high"
    },
    {
        "name": "SeniorCare Medical",
        "coverage_type": "medical",
        "eligibility": "50-80",
        "premium_min": 8000,
        "premium_max": 20000,
        "description": "Medical policy focused on older adults with chronic cover options.",
        "risk_tolerance": "low"
    },
    {
        "name": "Personal Accident Basic",
        "coverage_type": "accident,life",
        "eligibility": "16-70",
        "premium_min": 1000,
        "premium_max": 4000,
        "description": "Affordable accidental death and disability cover.",
        "risk_tolerance": "high"
    }
]

def init_db(db_path: str = DB_FILE, overwrite: bool = False) -> None:
    create_new = not os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # policies table
    c.execute("""
    CREATE TABLE IF NOT EXISTS policies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        coverage_type TEXT,
        eligibility TEXT,
        premium_min INTEGER,
        premium_max INTEGER,
        description TEXT,
        risk_tolerance TEXT
    );
    """)
    # clients table (stores client profiles and risk data)
    c.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        income REAL,
        dependents INTEGER,
        coverage TEXT,
        budget REAL,
        loss_ratio REAL,
        claims_history TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    # Seed sample policies if empty or overwrite requested
    c.execute("SELECT COUNT(*) FROM policies")
    count = c.fetchone()[0]
    if count == 0 or overwrite:
        if overwrite:
            c.execute("DELETE FROM policies")
        for p in SAMPLE_POLICIES:
            c.execute("""
            INSERT INTO policies (name, coverage_type, eligibility, premium_min, premium_max, description, risk_tolerance)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (p['name'], p['coverage_type'], p['eligibility'], p['premium_min'], p['premium_max'], p['description'], p['risk_tolerance']))
        conn.commit()
    conn.close()

def fetch_policies(db_path: str = DB_FILE):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id, name, coverage_type, eligibility, premium_min, premium_max, description, risk_tolerance FROM policies")
    rows = c.fetchall()
    conn.close()
    policies = []
    for r in rows:
        policies.append({
            "id": r[0],
            "name": r[1],
            "coverage_type": r[2],
            "eligibility": r[3],
            "premium_min": r[4],
            "premium_max": r[5],
            "description": r[6],
            "risk_tolerance": r[7]
        })
    return policies

def save_client(client, db_path: str = DB_FILE) -> int:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    claims_json = json.dumps(client.get('claims_history', {}))
    c.execute("""
        INSERT INTO clients (name, age, income, dependents, coverage, budget, loss_ratio, claims_history)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        client.get('name'),
        client.get('age'),
        client.get('income'),
        client.get('dependents'),
        client.get('coverage'),
        client.get('budget'),
        client.get('loss_ratio'),
        claims_json
    ))
    conn.commit()
    cid = c.lastrowid
    conn.close()
    return cid

if __name__ == '__main__':
    init_db()
    print('DB initialized and sample policies inserted.')
