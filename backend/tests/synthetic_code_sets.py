"""
Synthetic Code Sets for Testing Multi-Agentic Code Reviewer
Contains Easy, Medium, Hard, and Extreme examples of code to feed into the AI reviewer.
"""

EASY_CODE_SET = """
def calculate_average(numbers):
    total = sum(numbers)
    # Bug: Division by zero if list is empty
    # Quality: Missing type hints and docstring
    avg = total / len(numbers)
    return avg

print(calculate_average([1, 2, 3]))
print(calculate_average([]))
"""

MEDIUM_CODE_SET = """
import sqlite3

def get_user_data(user_id):
    # Security: SQL Injection vulnerability
    # Quality: No resource management (with statement)
    # Quality: Missing error handling
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    cursor.execute(query)
    data = cursor.fetchall()
    
    # Performance: Inefficient processing of data
    result = []
    for row in data:
        if row[1] == "active":
            result.append(row)
            
    return result
"""

HARD_CODE_SET = """
import threading
import time
from flask import Flask, request

app = Flask(__name__)
# Security: Hardcoded secret
SECRET_KEY = "my_super_secret_key_123"

# Quality/Concurrency: Shared mutable state without locks
request_count = 0
user_sessions = {}

@app.route('/login', methods=['POST'])
def login():
    global request_count
    request_count += 1
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Security: Timing attack vulnerability (naive string comparison)
    # Security: Plaintext password comparison
    if username == "admin" and password == "admin_pass":
        # Concurrency: Race condition
        session_id = str(time.time())
        user_sessions[session_id] = username
        
        # Performance/Architecture: Blocking sleep in a web request
        time.sleep(1) 
        return {"status": "success", "session": session_id}
        
    return {"status": "error"}

def background_cleanup():
    while True:
        # Quality: Modifying dictionary while iterating
        for session in user_sessions.keys():
            del user_sessions[session]
        time.sleep(60)

# Threading: Thread started but never joined/managed properly
threading.Thread(target=background_cleanup).start()
"""

EXTREME_CODE_SET = """
import os
import subprocess
import pickle
import base64
from fastapi import FastAPI, Header
import asyncio

app = FastAPI()

# Extreme complexity, multiple critical vulnerabilities, and bad practices

class DataProcessor:
    def __init__(self):
        self.cache = {}

    async def process_data(self, data_str: str):
        # Security: Insecure Deserialization (RCE)
        try:
            decoded = base64.b64decode(data_str)
            obj = pickle.loads(decoded)
        except Exception:
            # Quality: Bare except, silently passing errors
            pass
            
        # Security: Command Injection
        if "cmd" in obj:
            # Performance/Security: Shell=True and blocking call in async function
            os.system(f"echo Processing command: {obj['cmd']}")
            subprocess.Popen(obj['cmd'], shell=True)
            
        # Memory Leak: Appending to dict without bounds
        self.cache[len(self.cache)] = obj
        return self.cache

processor = DataProcessor()

@app.post("/api/v1/resource")
async def update_resource(payload: dict, x_api_key: str = Header(None)):
    # Security: Weak authorization / broken authentication
    if x_api_key != "static_dev_key":
        return {"error": "unauthorized"}

    # Performance: CPU bound task blocking event loop
    def heavy_computation():
        result = 0
        for i in range(10**8):
            result += i
        return result
        
    calc = heavy_computation()

    # Security: Path Traversal
    file_path = payload.get("log_file", "default.log")
    with open("/var/logs/" + file_path, "w") as f:
        f.write(f"Computation: {calc}")

    # Edge Case: Missing await for async function
    processor.process_data(payload.get("data", ""))
    
    return {"status": "processed", "calc": calc}
"""

SYNTHETIC_TEST_SUITE = {
    "easy": EASY_CODE_SET,
    "medium": MEDIUM_CODE_SET,
    "hard": HARD_CODE_SET,
    "extreme": EXTREME_CODE_SET
}
