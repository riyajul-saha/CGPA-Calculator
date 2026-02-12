import urllib.request
import json
import sqlite3
import time

# Wait for server to start if needed
time.sleep(2)

url = "http://127.0.0.1:5000/calculate_cgpa"
data = {
    "name": "Schema Test User",
    "roll": "999",
    "number": "888",
    "semester": 5,
    "sgpa1": 3.2,
    "credit1": 3,
    "sgpa2": 3.9,
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
            conn = sqlite3.connect('cgpa_db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            
            if row:
                print(f"Database insertion successful: {row}")
                # Schema: id, name, roll, number, semester, sgpa1, sgpa2, cgpa, created_at
                # Indices: 0, 1,    2,    3,      4,        5,     6,     7,    8
                
                name_match = row[1] == "Schema Test User"
                sgpa1_match = abs(row[5] - 3.2) < 0.01
                sgpa2_match = abs(row[6] - 3.9) < 0.01
                
                # Verify JSON message
                response_json = json.loads(response_body)
                msg_match = "message" in response_json and "successfully" in response_json["message"]
                
                if name_match and sgpa1_match and sgpa2_match and msg_match:
                    print(f"Data verification passed! sgpa1={row[5]}, sgpa2={row[6]}")
                    print(f"Message received: {response_json['message']}")
                else:
                    print(f"Data verification failed. Found: {row}")
                    print(f"Message check: {msg_match}")
            else:
                print("Database verification failed: No data found.")
                
        else:
            print("API request failed.")

except Exception as e:
    print(f"Test failed with error: {e}")
