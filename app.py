from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Database Configuration
DB_NAME = 'cgpa_db.sqlite'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll TEXT,
            number TEXT,
            semester INTEGER,
            cgpa REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on start
with app.app_context():
    init_db()

@app.route("/")
def calculator():
    return render_template("index.html")

@app.route("/calculate_cgpa", methods=["POST"])
def calculate_cgpa():
    try:
        data = request.get_json()
        sgpa1 = float(data.get('sgpa1', 0))
        sgpa2 = float(data.get('sgpa2', 0))
        credit1 = int(data.get('credit1', 1)) # Default to 1 to avoid division by zero
        credit2 = int(data.get('credit2', 1))

        if credit1 <= 0: credit1 = 1
        if credit2 <= 0: credit2 = 1

        total_points = (sgpa1 * credit1) + (sgpa2 * credit2)
        total_credits = credit1 + credit2
        
        cgpa_val = total_points / total_credits
        
        # --- Database Insertion ---
        try:
            conn = get_db_connection()
            
            # Insert data
            query = "INSERT INTO students (name, roll, number, semester, cgpa) VALUES (?, ?, ?, ?, ?)"
            values = (
                data.get('name', ''),
                data.get('roll', ''),
                data.get('number', ''),
                data.get('semester', 0),
                cgpa_val
            )
            conn.execute(query, values)
            conn.commit()
            conn.close()
            print("Data saved to database successfully.")
            
        except sqlite3.Error as err:
            print(f"Database Error: {err}")
            # Continue to return CGPA even if DB save fails
            
        return jsonify({"cgpa": f"{cgpa_val:.2f}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
