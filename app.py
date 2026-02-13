from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

# Database Configuration
DB_NAME = 'cgpa_db.sqlite'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

import sys

def init_db():
    try:
        conn = get_db_connection()
        print("Initializing Database...", file=sys.stderr)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS students (
                rollnumber TEXT PRIMARY KEY,
                name TEXT,
                semester INTEGER,
                sgpa1 REAL,
                sgpa2 REAL,
                cgpa REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print("Database initialized successfully.", file=sys.stderr)
    except Exception as e:
        print(f"Error initializing database: {e}", file=sys.stderr)

# Initialize DB on start
with app.app_context():
    init_db()

@app.route("/")
def calculator():
    return render_template("index.html")

@app.route("/calculate_cgpa", methods=["POST"])
def calculate_cgpa():
    init_db()  # Ensure table exists
    try:
        data = request.get_json()
        sgpa1 = float(data.get('sgpa1', 0))
        sgpa2 = float(data.get('sgpa2', 0))
        credit1 = int(data.get('credit1', 1)) 
        credit2 = int(data.get('credit2', 1))

        if credit1 <= 0: credit1 = 1
        if credit2 <= 0: credit2 = 1

        total_points = (sgpa1 * credit1) + (sgpa2 * credit2)
        total_credits = credit1 + credit2
        
        cgpa_val = total_points / total_credits
        
        # --- Database Logic ---
        try:
            conn = get_db_connection()
            
            # 1. Construct Primary Key
            roll = data.get('roll', '').strip()
            number = data.get('number', '').strip()
            rollnumber = f"{roll}{number}"
            
            # 2. Check existence
            existing_user = conn.execute("SELECT * FROM students WHERE rollnumber = ?", (rollnumber,)).fetchone()
            
            # 3. Handle Confirmation Logic
            confirmation = data.get('confirmation', 'No')
            message = "Calculated."
            should_update = False
            
            # Time setup
            ist_offset = timedelta(hours=5, minutes=30)
            ist_tz = timezone(ist_offset)
            now_ist = datetime.now(ist_tz)
            formatted_time = now_ist.strftime('%Y-%m-%d %H:%M:%S')

            if existing_user:
                if confirmation == "Yes":
                    # User confirmed overwrite
                    update_query = '''
                        UPDATE students 
                        SET name = ?, semester = ?, sgpa1 = ?, sgpa2 = ?, cgpa = ?, created_at = ?
                        WHERE rollnumber = ?
                    '''
                    update_values = (
                        data.get('name', ''),
                        data.get('semester', 0),
                        sgpa1,
                        sgpa2,
                        cgpa_val,
                        formatted_time,
                        rollnumber
                    )
                    conn.execute(update_query, update_values)
                    message = "Data updated successfully! 🔄"
                    print(f"Updated record for {rollnumber}")
                
                else:
                    # User exists but hasn't confirmed yet -> Return special status
                    conn.close()
                    return jsonify({
                        "cgpa": f"{cgpa_val:.2f}",
                        "exists": True,
                        "name": existing_user['name'],
                        "message": "User already exists."
                    })
            else:
                # New User -> Insert
                insert_query = "INSERT INTO students (rollnumber, name, semester, sgpa1, sgpa2, cgpa, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)"
                insert_values = (
                    rollnumber,
                    data.get('name', ''),
                    data.get('semester', 0),
                    sgpa1,
                    sgpa2,
                    cgpa_val,
                    formatted_time
                )
                conn.execute(insert_query, insert_values)
                message = "Data saved successfully! ✅"
                print(f"Created new record for {rollnumber}")

            conn.commit()
            conn.close()
            
        except sqlite3.Error as err:
            print(f"Database Error: {err}", file=sys.stderr)
            message = "Calculated, but database error occur."
            
        return jsonify({
            "cgpa": f"{cgpa_val:.2f}",
            "message": message
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
