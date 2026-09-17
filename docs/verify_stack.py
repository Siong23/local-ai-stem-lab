import json
import os
import sys
import urllib.error
import urllib.request
 
BASE = os.getenv("GATEWAY_URL", "http://127.0.0.1:8000")
GROUP = os.getenv("GROUP_ID", "GROUP01")
 
 
def request(path, method="GET", body=None):
    data = None if body is None else json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=12) as response:
        return response.status, json.load(response)
 
 
tests = [
    ("health", "/health", "GET", None),
    ("light", f"/v1/devices/{GROUP}/command", "POST", {"action":"read_light"}),
    ("icon", f"/v1/devices/{GROUP}/command", "POST", {"action":"show_icon","icon":"HAPPY"}),
]
 
failed = 0
for name, path, method, body in tests:
    try:
        status, result = request(path, method, body)
        ok = status == 200 and result.get("status") == "ok"
        print(("PASS" if ok else "FAIL"), name, json.dumps(result))
        failed += 0 if ok else 1
    except Exception as exc:
        print("FAIL", name, repr(exc))
        failed += 1
sys.exit(1 if failed else 0)
