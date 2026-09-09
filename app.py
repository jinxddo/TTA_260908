import os
from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client

app = Flask(__name__)

SUPABASE_URL = "https://pyotrqmsscvrunfdktxv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB5b3RycW1zc2N2cnVuZmRrdHh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg5MTQ4MzIsImV4cCI6MjEwNDQ5MDgzMn0.WCIWC8JCJsGMYZO37Azls_68zxbT-SH4wGKT8XntHyE"

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def index():
    todos = []
    try:
        supabase = get_supabase()
        res = supabase.table("todos").select("*").order("id", desc=False).execute()
        todos = res.data if res.data else []
    except Exception as e:
        # DB 에러 발생 시 서버를 멈추지 않고 화면에 에러를 출력
        return f"<div style='padding:20px; font-family:sans-serif;'><h2>⚠️ 데이터베이스 연결 오류</h2><p><b>원인:</b> {str(e)}</p></div>"
        
    return render_template("index.html", todos=todos)

@app.route("/add", methods=["POST"])
def add_todo():
    title = request.form.get("title")
    if title:
        try:
            supabase = get_supabase()
            supabase.table("todos").insert({"title": title, "completed": False}).execute()
        except Exception as e:
            print("Add Todo Error:", e)
    return redirect(url_for("index"))

@app.route("/toggle/<int:todo_id>")
def toggle_todo(todo_id):
    try:
        supabase = get_supabase()
        res = supabase.table("todos").select("completed").eq("id", todo_id).execute()
        if res.data:
            current_status = res.data[0]["completed"]
            supabase.table("todos").update({"completed": not current_status}).eq("id", todo_id).execute()
    except Exception as e:
        print("Toggle Todo Error:", e)
    return redirect(url_for("index"))

@app.route("/delete/<int:todo_id>")
def delete_todo(todo_id):
    try:
        supabase = get_supabase()
        supabase.table("todos").delete().eq("id", todo_id).execute()
    except Exception as e:
        print("Delete Todo Error:", e)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)