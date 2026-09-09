/**
 * TaskPulse - Modern To-Do Application Frontend Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // --- State Variables ---
  let state = {
    status: "all",
    category: "전체",
    priority: "전체",
    search: "",
  };

  // --- DOM Elements ---
  const tasksListEl = document.getElementById("tasks-list");
  const emptyStateEl = document.getElementById("empty-state");
  const loadingEl = document.getElementById("tasks-loading");
  const listCountBadgeEl = document.getElementById("list-count-badge");

  // Stats
  const statTotalEl = document.getElementById("stat-total");
  const statPendingEl = document.getElementById("stat-pending");
  const statCompletedEl = document.getElementById("stat-completed");
  const statRateEl = document.getElementById("stat-rate");
  const progressBarFillEl = document.getElementById("progress-bar-fill");

  // Add Form
  const addForm = document.getElementById("add-todo-form");
  const taskTitleInput = document.getElementById("task-title-input");
  const taskDescInput = document.getElementById("task-desc-input");
  const taskCategoryInput = document.getElementById("task-category-input");
  const taskPriorityInput = document.getElementById("task-priority-input");
  const taskDueDateInput = document.getElementById("task-due-date-input");
  const categoryPillsContainer = document.getElementById("category-pills");
  const priorityPillsContainer = document.getElementById("priority-pills");

  // Search & Filters
  const searchInput = document.getElementById("search-input");
  const searchClearBtn = document.getElementById("search-clear-btn");
  const filterCategorySelect = document.getElementById("filter-category");
  const filterPrioritySelect = document.getElementById("filter-priority");
  const statusTabs = document.querySelectorAll(".tab-btn");

  // Theme & Header
  const themeToggleBtn = document.getElementById("theme-toggle-btn");
  const themeIcon = document.getElementById("theme-icon");
  const currentDateText = document.getElementById("current-date-text");

  // Edit Modal
  const editModal = document.getElementById("edit-modal");
  const editForm = document.getElementById("edit-todo-form");
  const editTaskIdInput = document.getElementById("edit-task-id");
  const editTaskTitle = document.getElementById("edit-task-title");
  const editTaskDesc = document.getElementById("edit-task-desc");
  const editTaskCategory = document.getElementById("edit-task-category");
  const editTaskPriority = document.getElementById("edit-task-priority");
  const editTaskDueDate = document.getElementById("edit-task-due-date");
  const modalCloseBtn = document.getElementById("modal-close-btn");
  const modalCancelBtn = document.getElementById("modal-cancel-btn");

  // Toast Container
  const toastContainer = document.getElementById("toast-container");

  // --- Initial Setup ---
  initDateHeader();
  initTheme();
  initPillSelectors();
  initEventListeners();
  loadData();

  // --- Date Formatter ---
  function initDateHeader() {
    const now = new Date();
    const options = { year: "numeric", month: "long", day: "numeric", weekday: "long" };
    currentDateText.textContent = `${now.toLocaleDateString("ko-KR", options)} | 활기찬 하루를 계획해보세요`;
    
    // Default add task due date to today
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, "0");
    const dd = String(now.getDate()).padStart(2, "0");
    taskDueDateInput.value = `${yyyy}-${mm}-${dd}`;
  }

  // --- Theme Toggle ---
  function initTheme() {
    const savedTheme = localStorage.getItem("taskpulse_theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    updateThemeIcon(savedTheme);

    themeToggleBtn.addEventListener("click", () => {
      const currentTheme = document.documentElement.getAttribute("data-theme");
      const nextTheme = currentTheme === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", nextTheme);
      localStorage.setItem("taskpulse_theme", nextTheme);
      updateThemeIcon(nextTheme);
      showToast(`${nextTheme === "dark" ? "다크" : "라이트"} 모드로 전환되었습니다.`, "info");
    });
  }

  function updateThemeIcon(theme) {
    if (theme === "dark") {
      themeIcon.className = "fa-solid fa-moon";
    } else {
      themeIcon.className = "fa-solid fa-sun";
    }
  }

  // --- Pill Selectors for New Task ---
  function initPillSelectors() {
    categoryPillsContainer.querySelectorAll(".pill").forEach((btn) => {
      btn.addEventListener("click", () => {
        categoryPillsContainer.querySelectorAll(".pill").forEach((p) => p.classList.remove("active"));
        btn.classList.add("active");
        taskCategoryInput.value = btn.dataset.value;
      });
    });

    priorityPillsContainer.querySelectorAll(".pill").forEach((btn) => {
      btn.addEventListener("click", () => {
        priorityPillsContainer.querySelectorAll(".pill").forEach((p) => p.classList.remove("active"));
        btn.classList.add("active");
        taskPriorityInput.value = btn.dataset.value;
      });
    });
  }

  // --- Event Listeners ---
  function initEventListeners() {
    // Add Todo Form Submit
    addForm.addEventListener("submit", handleAddTodo);

    // Search Input with Debounce
    let debounceTimer;
    searchInput.addEventListener("input", (e) => {
      clearTimeout(debounceTimer);
      const query = e.target.value.trim();
      searchClearBtn.style.display = query.length > 0 ? "block" : "none";
      debounceTimer = setTimeout(() => {
        state.search = query;
        fetchTodos();
      }, 250);
    });

    // Clear Search
    searchClearBtn.addEventListener("click", () => {
      searchInput.value = "";
      searchClearBtn.style.display = "none";
      state.search = "";
      fetchTodos();
      searchInput.focus();
    });

    // Status Tabs
    statusTabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        statusTabs.forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        state.status = tab.dataset.status;
        fetchTodos();
      });
    });

    // Dropdown Filters
    filterCategorySelect.addEventListener("change", (e) => {
      state.category = e.target.value;
      fetchTodos();
    });

    filterPrioritySelect.addEventListener("change", (e) => {
      state.priority = e.target.value;
      fetchTodos();
    });

    // Edit Modal Close Handlers
    modalCloseBtn.addEventListener("click", closeModal);
    modalCancelBtn.addEventListener("click", closeModal);
    editModal.addEventListener("click", (e) => {
      if (e.target === editModal) closeModal();
    });
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && editModal.classList.contains("show")) {
        closeModal();
      }
    });

    // Edit Form Submit
    editForm.addEventListener("submit", handleEditTodoSubmit);
  }

  // --- Data Loading ---
  async function loadData() {
    await Promise.all([fetchTodos(), fetchStats()]);
  }

  async function fetchTodos() {
    loadingEl.style.display = "flex";
    emptyStateEl.style.display = "none";

    try {
      const params = new URLSearchParams();
      if (state.status !== "all") params.append("status", state.status);
      if (state.category !== "전체") params.append("category", state.category);
      if (state.priority !== "전체") params.append("priority", state.priority);
      if (state.search) params.append("search", state.search);

      const res = await fetch(`/api/todos?${params.toString()}`);
      if (!res.ok) throw new Error("할일 목록 조회 실패");
      const todos = await res.json();

      renderTodoList(todos);
    } catch (err) {
      console.error(err);
      showToast("할일 목록을 불러오는 중 오류가 발생했습니다.", "error");
    } finally {
      loadingEl.style.display = "none";
    }
  }

  async function fetchStats() {
    try {
      const res = await fetch("/api/stats");
      if (!res.ok) throw new Error("통계 조회 실패");
      const stats = await res.json();

      statTotalEl.textContent = stats.total;
      statPendingEl.textContent = stats.pending;
      statCompletedEl.textContent = stats.completed;
      statRateEl.textContent = `${stats.completion_rate}%`;
      progressBarFillEl.style.width = `${stats.completion_rate}%`;
    } catch (err) {
      console.error("Stats error:", err);
    }
  }

  // --- Render Task Items ---
  function renderTodoList(todos) {
    tasksListEl.innerHTML = "";
    listCountBadgeEl.textContent = `${todos.length}개`;

    if (todos.length === 0) {
      emptyStateEl.style.display = "block";
      return;
    }

    emptyStateEl.style.display = "none";

    const todayStr = new Date().toISOString().slice(0, 10);

    todos.forEach((todo) => {
      const li = document.createElement("li");
      li.className = `task-item ${todo.completed ? "completed" : ""}`;
      li.id = `task-item-${todo.id}`;

      // Category styling class
      let catClass = "badge-cat-work";
      if (todo.category === "개인") catClass = "badge-cat-personal";
      else if (todo.category === "공부") catClass = "badge-cat-study";
      else if (todo.category === "기타") catClass = "badge-cat-etc";

      // Priority styling class
      let priClass = "badge-pri-medium";
      if (todo.priority === "높음") priClass = "badge-pri-high";
      else if (todo.priority === "낮음") priClass = "badge-pri-low";

      // Due date check
      let dueDateHtml = "";
      if (todo.due_date) {
        const isOverdue = !todo.completed && todo.due_date < todayStr;
        dueDateHtml = `
          <span class="badge badge-due-date ${isOverdue ? "overdue" : ""}">
            <i class="fa-regular fa-calendar-check"></i>
            ${todo.due_date} ${isOverdue ? "(기한 초과)" : ""}
          </span>
        `;
      }

      li.innerHTML = `
        <div class="task-checkbox-wrapper">
          <input 
            type="checkbox" 
            class="task-checkbox" 
            id="checkbox-task-${todo.id}"
            ${todo.completed ? "checked" : ""} 
            title="완료 여부 토글"
            aria-label="${escapeHtml(todo.title)} 완료 여부 토글"
          >
        </div>
        <div class="task-content">
          <div class="task-header-row">
            <span class="task-title">${escapeHtml(todo.title)}</span>
          </div>
          ${todo.description ? `<p class="task-desc">${escapeHtml(todo.description)}</p>` : ""}
          <div class="task-meta-row">
            <span class="badge ${catClass}">
              <i class="fa-solid fa-tag"></i> ${escapeHtml(todo.category)}
            </span>
            <span class="badge ${priClass}">
              <i class="fa-solid fa-flag"></i> ${escapeHtml(todo.priority)}
            </span>
            ${dueDateHtml}
          </div>
        </div>
        <div class="task-actions">
          <button 
            type="button" 
            class="action-btn edit-btn" 
            id="edit-btn-${todo.id}"
            title="할일 수정" 
            aria-label="할일 수정"
          >
            <i class="fa-regular fa-pen-to-square"></i>
          </button>
          <button 
            type="button" 
            class="action-btn delete-btn" 
            id="delete-btn-${todo.id}"
            title="할일 삭제" 
            aria-label="할일 삭제"
          >
            <i class="fa-regular fa-trash-can"></i>
          </button>
        </div>
      `;

      // Event: Checkbox Toggle
      const checkbox = li.querySelector(".task-checkbox");
      checkbox.addEventListener("change", () => handleToggleTodo(todo.id));

      // Event: Edit Button
      const editBtn = li.querySelector(".edit-btn");
      editBtn.addEventListener("click", () => openEditModal(todo));

      // Event: Delete Button
      const deleteBtn = li.querySelector(".delete-btn");
      deleteBtn.addEventListener("click", () => handleDeleteTodo(todo.id, todo.title));

      tasksListEl.appendChild(li);
    });
  }

  // --- Handlers: CRUD Operations ---
  async function handleAddTodo(e) {
    e.preventDefault();
    const title = taskTitleInput.value.trim();
    if (!title) {
      showToast("할일 제목을 입력해주세요.", "error");
      taskTitleInput.focus();
      return;
    }

    const payload = {
      title: title,
      description: taskDescInput.value.trim(),
      category: taskCategoryInput.value,
      priority: taskPriorityInput.value,
      due_date: taskDueDateInput.value,
    };

    try {
      const res = await fetch("/api/todos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "등록 실패");
      }

      taskTitleInput.value = "";
      taskDescInput.value = "";
      showToast(`'${title}' 할일이 추가되었습니다!`, "success");

      await loadData();
    } catch (err) {
      console.error(err);
      showToast(err.message || "할일 추가 중 문제가 발생했습니다.", "error");
    }
  }

  async function handleToggleTodo(id) {
    try {
      const res = await fetch(`/api/todos/${id}/toggle`, { method: "PATCH" });
      if (!res.ok) throw new Error("토글 처리 실패");
      const updated = await res.json();

      const itemEl = document.getElementById(`task-item-${id}`);
      if (itemEl) {
        if (updated.completed) {
          itemEl.classList.add("completed");
          showToast(`'${updated.title}' 할일을 완료했습니다! 🎉`, "success");
        } else {
          itemEl.classList.remove("completed");
          showToast(`'${updated.title}' 상태를 진행 중으로 변경했습니다.`, "info");
        }
      }

      await fetchStats();
      // If filtering by active or completed, refresh the view
      if (state.status !== "all") {
        await fetchTodos();
      }
    } catch (err) {
      console.error(err);
      showToast("할일 상태 변경에 실패했습니다.", "error");
      await fetchTodos();
    }
  }

  function openEditModal(todo) {
    editTaskIdInput.value = todo.id;
    editTaskTitle.value = todo.title;
    editTaskDesc.value = todo.description || "";
    editTaskCategory.value = todo.category || "업무";
    editTaskPriority.value = todo.priority || "보통";
    editTaskDueDate.value = todo.due_date || "";

    editModal.classList.add("show");
    editModal.setAttribute("aria-hidden", "false");
    editTaskTitle.focus();
  }

  function closeModal() {
    editModal.classList.remove("show");
    editModal.setAttribute("aria-hidden", "true");
  }

  async function handleEditTodoSubmit(e) {
    e.preventDefault();
    const id = editTaskIdInput.value;
    const title = editTaskTitle.value.trim();

    if (!title) {
      showToast("할일 제목은 필수입니다.", "error");
      editTaskTitle.focus();
      return;
    }

    const payload = {
      title: title,
      description: editTaskDesc.value.trim(),
      category: editTaskCategory.value,
      priority: editTaskPriority.value,
      due_date: editTaskDueDate.value,
    };

    try {
      const res = await fetch(`/api/todos/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "수정 실패");
      }

      closeModal();
      showToast("할일이 성공적으로 수정되었습니다.", "success");
      await loadData();
    } catch (err) {
      console.error(err);
      showToast(err.message || "할일 수정 중 문제가 발생했습니다.", "error");
    }
  }

  async function handleDeleteTodo(id, title) {
    if (!confirm(`'${title}' 할일을 정말 삭제하시겠습니까?`)) {
      return;
    }

    try {
      const res = await fetch(`/api/todos/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("삭제 실패");

      showToast(`'${title}' 할일이 삭제되었습니다.`, "info");
      await loadData();
    } catch (err) {
      console.error(err);
      showToast("할일 삭제 중 오류가 발생했습니다.", "error");
    }
  }

  // --- Toast Notification Helper ---
  function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    let iconClass = "fa-circle-info";
    if (type === "success") iconClass = "fa-circle-check";
    if (type === "error") iconClass = "fa-circle-exclamation";

    toast.innerHTML = `
      <i class="fa-solid ${iconClass} toast-icon"></i>
      <span>${escapeHtml(message)}</span>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.classList.add("fade-out");
      setTimeout(() => {
        toast.remove();
      }, 300);
    }, 3200);
  }

  // --- Utility: Escape HTML ---
  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
