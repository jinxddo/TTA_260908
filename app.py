import os
from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client

app = Flask(__name__)

# Vercel 환경변수에서 Supabase 정보 불러오기
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def index():
    todos = []
    if supabase:
        res = supabase.table("todos").select("*").order("id", desc=False).execute()
        todos = res.data if res.data else []
    return render_template("index.html", todos=todos)

@app.route("/add", methods=["POST"])
def add_todo():
    title = request.form.get("title")
    if title and supabase:
        supabase.table("todos").insert({"title": title, "completed": False}).execute()
    return redirect(url_for("index"))

@app.route("/toggle/<int:todo_id>")
def toggle_todo(todo_id):
    if supabase:
        res = supabase.table("todos").select("completed").eq("id", todo_id).execute()
        if res.data:
            current_status = res.data[0]["completed"]
            supabase.table("todos").update({"completed": not current_status}).eq("id", todo_id).execute()
    return redirect(url_for("index"))

@app.route("/delete/<int:todo_id>")
def delete_todo(todo_id):
    if supabase:
        supabase.table("todos").delete().eq("id", todo_id).execute()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)