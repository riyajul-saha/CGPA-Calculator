import urllib.request
import json
import sqlite3
import time

# Wait for server to start if needed (though it should be running)
time.sleep(2)

url = "http://127.0.0.1:5000/calculate_cgpa"
data = {
    "name": "Test User",
    "roll": "123",
    "number": "456",
    "semester": 3,
    "sgpa1": 3.5,
    "credit1": 4,
    "sgpa2": 3.8,
    "credit2": 4
}

json_data = json.dumps(data).encode('utf-8')
req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})

try:
    print(f"Sending POST request to {url}...")
    with urllib.request.urlopen(req) as response:
        status_code = response.getcode()
        response_body = response.read().decode('utf-8')
        print(f"Status Code: {status_code}")
        print(f"Response: {response_body}")

        if status_code == 200:
            print("API request successful.")
            
            # Verify database
            print("Verifying database content...")
            # Using absolute path just in case, or relative to cwd which is project root
            conn = sqlite3.connect('cgpa_db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            
            if row:
                print(f"Database insertion successful: {row}")
                # row index might differ based on exact schema order, but name is usually 2nd or so.
                # Schema: id, name, roll, number, semester, cgpa, created_at
                # Indices: 0, 1,    2,    3,      4,        5,    6
                if row[1] == "Test User" and row[3] == "456":
                    print("Data verification passed!")
                else:
                    print(f"Data verification failed: Mismatch. Found name={row[1]}, number={row[3]}")
            else:
                print("Database verification failed: No data found.")
                
        else:
            print("API request failed.")

except Exception as e:
    print(f"Test failed with error: {e}")
