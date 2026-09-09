import os
import sys
import tempfile
import unittest

# Add app directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TodoAppTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary database for isolated testing
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.environ["TODO_DB_PATH"] = self.db_path

        import app
        self.app_module = app
        self.app_module.DB_PATH = self.db_path
        self.app_module.init_db()

        self.client = self.app_module.app.test_client()
        self.client.testing = True

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass

    def test_index_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"TaskPulse", response.data)

    def test_create_and_get_todo(self):
        payload = {
            "title": "테스트 할일 항목",
            "description": "상세한 테스트 설명입니다.",
            "category": "업무",
            "priority": "높음",
            "due_date": "2026-12-31"
        }
        res = self.client.post("/api/todos", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data["title"], "테스트 할일 항목")
        self.assertEqual(data["priority"], "높음")
        todo_id = data["id"]

        # Fetch single todo
        res_single = self.client.get(f"/api/todos/{todo_id}")
        self.assertEqual(res_single.status_code, 200)
        single_data = res_single.get_json()
        self.assertEqual(single_data["title"], "테스트 할일 항목")

    def test_create_todo_validation(self):
        # Missing title
        res = self.client.post("/api/todos", json={"title": "   "})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("error", data)

    def test_toggle_todo(self):
        # Create
        res = self.client.post("/api/todos", json={"title": "토글 테스트"})
        todo_id = res.get_json()["id"]

        # Toggle to completed
        res_toggle = self.client.patch(f"/api/todos/{todo_id}/toggle")
        self.assertEqual(res_toggle.status_code, 200)
        self.assertEqual(res_toggle.get_json()["completed"], 1)

        # Toggle back to active
        res_toggle2 = self.client.patch(f"/api/todos/{todo_id}/toggle")
        self.assertEqual(res_toggle2.status_code, 200)
        self.assertEqual(res_toggle2.get_json()["completed"], 0)

    def test_update_todo(self):
        # Create
        res = self.client.post("/api/todos", json={"title": "수정 전 제목"})
        todo_id = res.get_json()["id"]

        # Update
        update_payload = {
            "title": "수정 후 제목",
            "description": "설명 업데이트",
            "category": "공부",
            "priority": "낮음",
            "due_date": "2026-10-15"
        }
        res_update = self.client.put(f"/api/todos/{todo_id}", json=update_payload)
        self.assertEqual(res_update.status_code, 200)
        updated = res_update.get_json()
        self.assertEqual(updated["title"], "수정 후 제목")
        self.assertEqual(updated["category"], "공부")
        self.assertEqual(updated["priority"], "낮음")

    def test_delete_todo(self):
        # Create
        res = self.client.post("/api/todos", json={"title": "삭제 대상 할일"})
        todo_id = res.get_json()["id"]

        # Delete
        res_del = self.client.delete(f"/api/todos/{todo_id}")
        self.assertEqual(res_del.status_code, 200)

        # Confirm 404
        res_get = self.client.get(f"/api/todos/{todo_id}")
        self.assertEqual(res_get.status_code, 404)

    def test_stats_and_filtering(self):
        # Initial stats
        res_stats = self.client.get("/api/stats")
        self.assertEqual(res_stats.status_code, 200)
        stats = res_stats.get_json()
        self.assertIn("total", stats)
        self.assertIn("completed", stats)
        self.assertIn("completion_rate", stats)

        # Filter by search
        res_search = self.client.get("/api/todos?search=기획서")
        self.assertEqual(res_search.status_code, 200)
        items = res_search.get_json()
        self.assertTrue(any("기획서" in item["title"] for item in items))


if __name__ == "__main__":
    unittest.main()
