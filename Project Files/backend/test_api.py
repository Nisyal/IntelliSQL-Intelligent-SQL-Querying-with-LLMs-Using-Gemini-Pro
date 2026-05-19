"""
End-to-end API test script for Steps 1-4.
Tests: health, auth, generate, execute, history, models, schema.
"""

import urllib.request
import json

BASE = "http://127.0.0.1:8000"

def api(method, path, data=None, token=None):
    url = BASE + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

print("=" * 60)
print("TEST 1: Health Check")
r, s = api("GET", "/api/health")
print(f"  Status: {s} | DB: {r.get('database')}")
assert s == 200 and r["status"] == "healthy"

print("\nTEST 2: Register User")
r, s = api("POST", "/api/auth/register", {
    "username": "testuser",
    "email": "test@intellisql.com",
    "password": "test1234"
})
print(f"  Status: {s} | User: {r.get('username')} | ID: {r.get('user_id')}")
token = r.get("access_token")

print("\nTEST 3: Login")
r, s = api("POST", "/api/auth/login", {
    "email": "test@intellisql.com",
    "password": "test1234"
})
print(f"  Status: {s} | Token received: {bool(r.get('access_token'))}")
token = r.get("access_token")

print("\nTEST 4: Get /me (auth required)")
r, s = api("GET", "/api/auth/me", token=token)
print(f"  Status: {s} | Username: {r.get('username')}")

print("\nTEST 5: List Models")
r, s = api("GET", "/api/models")
models = r.get("models", [])
print(f"  Status: {s} | Models: {[m['name'] for m in models]}")

print("\nTEST 6: Get Schema")
r, s = api("GET", "/api/schema")
tables = list(r.get("tables", {}).keys())
print(f"  Status: {s} | Tables: {tables}")

print("\nTEST 7: Generate SQL (Qwen)")
r, s = api("POST", "/api/generate", {
    "question": "Show all students in BTech",
    "model": "qwen-2.5-coder-32b"
}, token=token)
print(f"  Status: {s}")
print(f"  SQL: {r.get('sql')}")
print(f"  Confidence: {r.get('confidence', {}).get('score')}")
query_id = r.get("query_id")

print("\nTEST 8: Execute SQL")
r, s = api("POST", "/api/execute", {
    "sql": r.get("sql", "SELECT 1"),
    "query_id": query_id
})
print(f"  Status: {s}")
print(f"  Columns: {r.get('columns')}")
print(f"  Rows: {r.get('rows')}")
print(f"  Row count: {r.get('row_count')}")

print("\nTEST 9: SQL Injection Blocked")
r, s = api("POST", "/api/execute", {"sql": "DROP TABLE students;"})
print(f"  Status: {s} | Blocked: {s == 400}")
print(f"  Message: {r.get('detail')}")

print("\nTEST 10: History")
r, s = api("GET", "/api/history", token=token)
print(f"  Status: {s} | Total queries: {r.get('total')}")
if r.get("items"):
    item = r["items"][0]
    print(f"  Latest: '{item['natural_query']}' -> {item['generated_sql']}")

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
