import os
from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client

app = Flask(__name__)

# 정확하게 찾으신 URL과 Legacy anon 키 적용!
SUPABASE_URL = "https://pyotrqmsscvrunfdktxv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB5b3RycW1zc2N2cnVuZmRrdHh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg5MTQ4MzIsImV4cCI6MjEwNDQ5MDgzMn0.WCIWC8JCJsGMYZO37Azls_68zxbT-SH4wGKT8XntHyE"

# Supabase 클라이언트 연결
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def index():
    todos = []
    try:
        # DB에서 할 일 목록 가져오기 (id 순 정렬)
        res = supabase.table("todos").select("*").order("id", desc=False).execute()
        todos = res.data if res.data else []
    except Exception as e:
        # 혹시라도 에러가 나면 화면에 표시 (500 에러 방지)
        return f"<h2 style='color:red;'>데이터베이스 연결 에러: {str(e)}</h2><p>에러가 지속되면 알려주세요!</p>"
        
    return render_template("index.html", todos=todos)

@app.route("/add", methods=["POST"])
def add_todo():
    title = request.form.get("title")
    if title:
        supabase.table("todos").insert({"title": title, "completed": False}).execute()
    return redirect(url_for("index"))

@app.route("/toggle/<int:todo_id>")
def toggle_todo(todo_id):
    res = supabase.table("todos").select("completed").eq("id", todo_id).execute()
    if res.data:
        current_status = res.data[0]["completed"]
        supabase.table("todos").update({"completed": not current_status}).eq("id", todo_id).execute()
    return redirect(url_for("index"))

@app.route("/delete/<int:todo_id>")
def delete_todo(todo_id):
    supabase.table("todos").delete().eq("id", todo_id).execute()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)