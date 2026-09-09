import json
import urllib.request
import urllib.parse
import sys

BASE_URL = "http://127.0.0.1:5000"

def request(path, method="GET", data=None):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
        encoded = json.dumps(data).encode("utf-8")
        req.data = encoded
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            content_type = resp.headers.get("Content-Type", "")
            body = resp.read().decode("utf-8")
            return status, content_type, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return e.code, "", body

def run_checks():
    print("=== LIVE SERVER VERIFICATION START ===")
    
    # 1. Check HTML Page
    status, ctype, body = request("/")
    assert status == 200, f"Expected 200, got {status}"
    assert "TaskPulse" in body, "TaskPulse title missing from HTML"
    assert "id=\"add-todo-form\"" in body, "Form missing"
    print("✔ GET / (HTML Index) -> 200 OK & Content verified")

    # 2. Check Static Assets
    status, ctype, body = request("/static/css/style.css")
    assert status == 200, f"CSS failed with {status}"
    assert "TaskPulse" in body, "CSS content missing"
    print("✔ GET /static/css/style.css -> 200 OK")

    status, ctype, body = request("/static/js/main.js")
    assert status == 200, f"JS failed with {status}"
    assert "DOMContentLoaded" in body, "JS content missing"
    print("✔ GET /static/js/main.js -> 200 OK")

    # 3. Check Initial List
    status, _, body = request("/api/todos")
    assert status == 200, f"Expected 200, got {status}"
    todos = json.loads(body)
    assert isinstance(todos, list), "Expected list of todos"
    initial_count = len(todos)
    print(f"✔ GET /api/todos -> 200 OK (Found {initial_count} items)")

    # 4. Create New Task
    new_task = {
        "title": "라이브 서버 E2E 테스트 항목",
        "description": "자동화 검증 스크립트로 등록된 할일",
        "category": "공부",
        "priority": "높음",
        "due_date": "2026-09-30"
    }
    status, _, body = request("/api/todos", method="POST", data=new_task)
    assert status == 201, f"Expected 201, got {status}"
    created = json.loads(body)
    task_id = created["id"]
    assert created["title"] == new_task["title"]
    print(f"✔ POST /api/todos -> 201 Created (ID: {task_id})")

    # 5. Toggle Task Completed
    status, _, body = request(f"/api/todos/{task_id}/toggle", method="PATCH")
    assert status == 200, f"Expected 200, got {status}"
    toggled = json.loads(body)
    assert toggled["completed"] == 1, "Expected completed to be 1"
    print(f"✔ PATCH /api/todos/{task_id}/toggle -> 200 OK (Completed: {toggled['completed']})")

    # 6. Update Task
    update_data = {
        "title": "라이브 서버 E2E 테스트 항목 [수정완료]",
        "description": "설명이 정상적으로 수정되었습니다.",
        "category": "업무",
        "priority": "보통",
        "due_date": "2026-10-01"
    }
    status, _, body = request(f"/api/todos/{task_id}", method="PUT", data=update_data)
    assert status == 200, f"Expected 200, got {status}"
    updated = json.loads(body)
    assert updated["title"] == update_data["title"]
    assert updated["category"] == "업무"
    print(f"✔ PUT /api/todos/{task_id} -> 200 OK (Updated title & category)")

    # 7. Check Stats API
    status, _, body = request("/api/stats")
    assert status == 200, f"Expected 200, got {status}"
    stats = json.loads(body)
    assert "total" in stats and "completed" in stats and "completion_rate" in stats
    print(f"✔ GET /api/stats -> 200 OK (Total: {stats['total']}, Completed: {stats['completed']}, Rate: {stats['completion_rate']}%)")

    # 8. Delete Created Task
    status, _, body = request(f"/api/todos/{task_id}", method="DELETE")
    assert status == 200, f"Expected 200, got {status}"
    print(f"✔ DELETE /api/todos/{task_id} -> 200 OK")

    # 9. Verify 404 after deletion
    status, _, _ = request(f"/api/todos/{task_id}")
    assert status == 404, f"Expected 404, got {status}"
    print(f"✔ GET /api/todos/{task_id} (Post-delete check) -> 404 Not Found")

    print("\n🎉 ALL LIVE SERVER INTEGRATION TESTS PASSED SUCCESSFULLY! 🎉")

if __name__ == "__main__":
    run_checks()
