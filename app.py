import os
import sqlite3
from datetime import datetime
from flask import Flask, g, jsonify, render_template, request

app = Flask(__name__)
DB_PATH = os.environ.get("TODO_DB_PATH", os.path.join(os.path.dirname(__file__), "todos.db"))


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                category TEXT DEFAULT '업무',
                priority TEXT DEFAULT '보통',
                due_date TEXT DEFAULT '',
                completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT
            )
        """)
        # Insert initial sample data if empty
        cursor = conn.execute("SELECT COUNT(*) FROM todos")
        count = cursor.fetchone()[0]
        if count == 0:
            sample_todos = [
                (
                    "프로젝트 기획서 초안 작성",
                    "Q3 신규 기능 로드맵 및 일정 정리하기",
                    "업무",
                    "높음",
                    datetime.now().strftime("%Y-%m-%d"),
                    0,
                    datetime.now().isoformat(),
                    None,
                ),
                (
                    "주간 파이썬 스터디 발표 준비",
                    "Flask RESTful API 설계 및 비동기 통신 주제",
                    "공부",
                    "보통",
                    datetime.now().strftime("%Y-%m-%d"),
                    1,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
                (
                    "헬스장 정기 운동 가기",
                    "상체 웨이트 트레이닝 및 유산소 30분",
                    "개인",
                    "낮음",
                    datetime.now().strftime("%Y-%m-%d"),
                    0,
                    datetime.now().isoformat(),
                    None,
                ),
            ]
            conn.executemany(
                """
                INSERT INTO todos (title, description, category, priority, due_date, completed, created_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                sample_todos,
            )
        conn.commit()
    finally:
        conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/todos", methods=["GET"])
def get_todos():
    status = request.args.get("status", "all")  # all, active, completed
    category = request.args.get("category")
    priority = request.args.get("priority")
    search = request.args.get("search", "").strip()

    query = "SELECT * FROM todos WHERE 1=1"
    params = []

    if status == "active":
        query += " AND completed = 0"
    elif status == "completed":
        query += " AND completed = 1"

    if category and category != "전체":
        query += " AND category = ?"
        params.append(category)

    if priority and priority != "전체":
        query += " AND priority = ?"
        params.append(priority)

    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard])

    query += " ORDER BY completed ASC, CASE priority WHEN '높음' THEN 1 WHEN '보통' THEN 2 WHEN '낮음' THEN 3 ELSE 4 END, id DESC"

    with get_db() as conn:
        todos = conn.execute(query, params).fetchall()
        return jsonify([dict(row) for row in todos])


@app.route("/api/todos", methods=["POST"])
def create_todo():
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "할일 제목을 입력해주세요."}), 400

    description = data.get("description", "").strip()
    category = data.get("category", "업무").strip()
    priority = data.get("priority", "보통").strip()
    due_date = data.get("due_date", "").strip()
    now_str = datetime.now().isoformat()

    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO todos (title, description, category, priority, due_date, completed, created_at)
            VALUES (?, ?, ?, ?, ?, 0, ?)
        """,
            (title, description, category, priority, due_date, now_str),
        )
        todo_id = cursor.lastrowid
        conn.commit()
        new_todo = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        return jsonify(dict(new_todo)), 201


@app.route("/api/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    with get_db() as conn:
        todo = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if not todo:
            return jsonify({"error": "해당 할일을 찾을 수 없습니다."}), 404
        return jsonify(dict(todo))


@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "할일 제목을 입력해주세요."}), 400

    description = data.get("description", "").strip()
    category = data.get("category", "업무").strip()
    priority = data.get("priority", "보통").strip()
    due_date = data.get("due_date", "").strip()

    with get_db() as conn:
        cursor = conn.execute(
            """
            UPDATE todos
            SET title = ?, description = ?, category = ?, priority = ?, due_date = ?
            WHERE id = ?
        """,
            (title, description, category, priority, due_date, todo_id),
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "해당 할일을 찾을 수 없습니다."}), 404
        conn.commit()
        updated = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        return jsonify(dict(updated))


@app.route("/api/todos/<int:todo_id>/toggle", methods=["PATCH"])
def toggle_todo(todo_id):
    with get_db() as conn:
        todo = conn.execute("SELECT completed FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if not todo:
            return jsonify({"error": "해당 할일을 찾을 수 없습니다."}), 404

        new_status = 1 if todo["completed"] == 0 else 0
        completed_at = datetime.now().isoformat() if new_status == 1 else None

        conn.execute(
            """
            UPDATE todos
            SET completed = ?, completed_at = ?
            WHERE id = ?
        """,
            (new_status, completed_at, todo_id),
        )
        conn.commit()
        updated = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        return jsonify(dict(updated))


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "해당 할일을 찾을 수 없습니다."}), 404
        conn.commit()
        return jsonify({"success": True, "message": "성공적으로 삭제되었습니다."})


@app.route("/api/stats", methods=["GET"])
def get_stats():
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM todos").fetchone()[0]
        completed = conn.execute("SELECT COUNT(*) FROM todos WHERE completed = 1").fetchone()[0]
        pending = total - completed
        rate = round((completed / total * 100), 1) if total > 0 else 0

        # Category counts
        cat_counts = conn.execute("""
            SELECT category, COUNT(*) as cnt FROM todos GROUP BY category
        """).fetchall()

        # Priority counts
        pri_counts = conn.execute("""
            SELECT priority, COUNT(*) as cnt FROM todos WHERE completed = 0 GROUP BY priority
        """).fetchall()

        return jsonify({
            "total": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": rate,
            "categories": {row["category"]: row["cnt"] for row in cat_counts},
            "priorities": {row["priority"]: row["cnt"] for row in pri_counts},
        })


# Initialize DB when running or importing
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
