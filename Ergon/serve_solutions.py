"""
Simple server to serve solutions for testing
"""

from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
CORS(app)

@app.route('/api/v1/solutions', methods=['GET'])
def get_solutions():
    """Get all solutions from database"""
    try:
        conn = sqlite3.connect('ergon.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, type, description, capabilities, 
                   usage_count, success_rate
            FROM solutions
            ORDER BY usage_count DESC
        """)
        
        solutions = []
        for row in cursor.fetchall():
            solution = dict(row)
            # Parse JSON fields
            solution['capabilities'] = json.loads(solution['capabilities'])
            solutions.append(solution)
            
        conn.close()
        
        return jsonify({
            "solutions": solutions,
            "total": len(solutions)
        })
    except Exception as e:
        return jsonify({
            "solutions": [],
            "error": str(e)
        })

if __name__ == '__main__':
    print("Serving solutions on http://localhost:8102/api/v1/solutions")
    app.run(port=8102, debug=True)