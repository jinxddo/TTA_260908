import os
from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client

app = Flask(__name__)

# 전달해주신 Supabase 접속 정보 적용 (URL 끝의 /rest/v1/ 은 제외해야 정상 작동합니다)
SUPABASE_URL = "https://pyotrqmsscvrunfdktxv.supabase.co"
SUPABASE_KEY = "sb_publishable_DdkQ6RcMsCNvBHzlyLXbRA_9HRhZQJo"

# Supabase 클라이언트 연결
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def index():
    todos = []
    try:
        # DB에서 할 일 목록 가져오기
        res = supabase.table("todos").select("*").order("id", desc=False).execute()
        todos = res.data if res.data else []
    except Exception as e:
        # 에러 발생 시 화면에 출력하여 원인 파악
        return f"<h2 style='color:red;'>데이터베이스 연결 에러: {str(e)}</h2><p>Supabase의 RLS(보안설정)가 해제되어 있는지 확인하세요.</p>"
        
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