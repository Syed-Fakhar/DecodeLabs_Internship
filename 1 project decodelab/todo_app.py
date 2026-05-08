"""
=============================================================
  To-Do List Manager
  Data Management Project — IPO Model Demo
  Data Structures Used: List (database) + Dictionary (record)
=============================================================
  INPUT   → User enters a task name
  PROCESS → Task stored as dict inside a list; saved to JSON
  OUTPUT  → GUI updated dynamically to reflect current state
=============================================================
"""

import json
import os
import customtkinter as ctk
from tkinter import messagebox

# ─────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────
DATA_FILE = "tasks.json"          # JSON persistence file
ctk.set_appearance_mode("dark")   # "dark" | "light" | "system"
ctk.set_default_color_theme("blue")

# ─────────────────────────────────────────────
#  DATA LAYER  (List of Dictionaries)
# ─────────────────────────────────────────────
#  tasks = [
#      { "id": 1, "task_name": "Buy groceries", "completed": False },
#      { "id": 2, "task_name": "Read a book",   "completed": True  },
#      ...
#  ]
# ─────────────────────────────────────────────
tasks: list[dict] = []    # Global list acting as our in-memory database


def load_tasks() -> None:
    """
    INPUT   : JSON file on disk (if it exists)
    PROCESS : Parse JSON → Python list of dicts
    OUTPUT  : Populate the global `tasks` list
    """
    global tasks
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                tasks = json.load(f)
        except (json.JSONDecodeError, IOError):
            tasks = []
    else:
        tasks = []


def save_tasks() -> None:
    """
    INPUT   : Current state of global `tasks` list
    PROCESS : Serialize list → JSON string
    OUTPUT  : Write JSON to DATA_FILE
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)


def _next_id() -> int:
    """Return a unique ID one higher than the current maximum."""
    return max((t["id"] for t in tasks), default=0) + 1


# ─────────────────────────────────────────────
#  TASK OPERATIONS
# ─────────────────────────────────────────────

def add_task(task_name: str) -> tuple[bool, str]:
    """
    INPUT   : task_name – string from entry widget
    PROCESS : Validate → build dict → append to list → save
    OUTPUT  : (success: bool, message: str)
    """
    task_name = task_name.strip()
    if not task_name:
        return False, "Task name cannot be empty."
    if len(task_name) > 200:
        return False, "Task name is too long (max 200 characters)."

    # Build a single task record (dictionary)
    new_task: dict = {
        "id":         _next_id(),
        "task_name":  task_name,
        "completed":  False
    }
    tasks.append(new_task)   # Store dict inside the list
    save_tasks()
    return True, f'Task "{task_name}" added successfully.'


def delete_task(task_id: int) -> tuple[bool, str]:
    """
    INPUT   : task_id – integer ID of the task to remove
    PROCESS : Find dict in list → remove → save
    OUTPUT  : (success: bool, message: str)
    """
    global tasks
    original_len = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    if len(tasks) < original_len:
        save_tasks()
        return True, "Task deleted."
    return False, "Task not found."


def mark_completed(task_id: int) -> tuple[bool, str]:
    """
    INPUT   : task_id – integer ID of the task to mark done
    PROCESS : Find dict in list → set completed=True → save
    OUTPUT  : (success: bool, message: str)
    """
    for task in tasks:
        if task["id"] == task_id:
            if task["completed"]:
                return False, "Task is already marked as completed."
            task["completed"] = True
            save_tasks()
            return True, "Task marked as completed ✔"
    return False, "Task not found."


def clear_all_tasks() -> tuple[bool, str]:
    """
    INPUT   : (none — acts on global list)
    PROCESS : Empty the list → save
    OUTPUT  : (success: bool, message: str)
    """
    global tasks
    if not tasks:
        return False, "There are no tasks to clear."
    tasks.clear()
    save_tasks()
    return True, "All tasks cleared."


# ─────────────────────────────────────────────
#  GUI CLASS
# ─────────────────────────────────────────────

class ToDoApp(ctk.CTk):
    """Main application window."""

    # ── Colour palette ──────────────────────────────────────────────────
    CLR_BG          = "#0f1117"
    CLR_CARD        = "#1a1d2e"
    CLR_ACCENT      = "#6c63ff"
    CLR_ACCENT2     = "#ff6584"
    CLR_SUCCESS     = "#43d9ad"
    CLR_WARN        = "#ffd166"
    CLR_TEXT        = "#e2e8f0"
    CLR_MUTED       = "#8892a4"
    CLR_DONE_BG     = "#1e2d25"
    CLR_DONE_TEXT   = "#43d9ad"
    CLR_HOVER       = "#2a2d3e"

    def __init__(self):
        super().__init__()

        # ── Window setup ────────────────────────────────────────────────
        self.title("To-Do List Manager")
        self.geometry("780x640")
        self.minsize(680, 540)
        self.configure(fg_color=self.CLR_BG)
        self.resizable(True, True)

        # Tracks which task ID is selected in the list
        self._selected_task_id: int | None = None

        self._build_ui()
        load_tasks()
        self.display_tasks()

    # ── UI Construction ─────────────────────────────────────────────────

    def _build_ui(self):
        """Assemble all widgets."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_input_row()
        self._build_task_list()
        self._build_action_bar()
        self._build_status_bar()

    def _build_header(self):
        """Top branding / title strip."""
        header = ctk.CTkFrame(self, fg_color=self.CLR_CARD, corner_radius=0, height=70)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        header.grid_propagate(False)

        ctk.CTkLabel(
            header,
            text="✅  To-Do List Manager",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=self.CLR_TEXT,
        ).grid(row=0, column=0, padx=24, pady=12, sticky="w")

        self.counter_label = ctk.CTkLabel(
            header,
            text="0 tasks",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.CLR_MUTED,
        )
        self.counter_label.grid(row=0, column=1, padx=24, pady=12, sticky="e")

    def _build_input_row(self):
        """Entry field + Add button row."""
        frame = ctk.CTkFrame(self, fg_color=self.CLR_CARD, corner_radius=12)
        frame.grid(row=1, column=0, padx=20, pady=(14, 6), sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        # Task entry
        self.task_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Enter a new task…",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            height=44,
            corner_radius=10,
            border_width=2,
            border_color=self.CLR_ACCENT,
            fg_color="#12141f",
            text_color=self.CLR_TEXT,
        )
        self.task_entry.grid(row=0, column=0, padx=(16, 10), pady=14, sticky="ew")
        self.task_entry.bind("<Return>", lambda e: self._on_add())   # Enter key shortcut

        # Add button
        self.add_btn = ctk.CTkButton(
            frame,
            text="＋  Add Task",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=44,
            width=130,
            corner_radius=10,
            fg_color=self.CLR_ACCENT,
            hover_color="#5a52d5",
            command=self._on_add,
        )
        self.add_btn.grid(row=0, column=1, padx=(0, 16), pady=14)

    def _build_task_list(self):
        """Scrollable card list of tasks."""
        # Outer container
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.grid(row=2, column=0, padx=20, pady=4, sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        # Scrollable inner frame
        self.scroll_frame = ctk.CTkScrollableFrame(
            outer,
            fg_color=self.CLR_CARD,
            corner_radius=12,
            scrollbar_button_color=self.CLR_ACCENT,
            scrollbar_button_hover_color="#5a52d5",
        )
        self.scroll_frame.grid(row=0, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # Placeholder shown when list is empty
        self.placeholder_label = ctk.CTkLabel(
            self.scroll_frame,
            text="📋  No tasks yet. Add your first task above!",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=self.CLR_MUTED,
        )

        # We store card widgets here so we can destroy & rebuild efficiently
        self._task_cards: list[ctk.CTkFrame] = []

    def _build_action_bar(self):
        """Bottom row of action buttons."""
        bar = ctk.CTkFrame(self, fg_color=self.CLR_CARD, corner_radius=12)
        bar.grid(row=3, column=0, padx=20, pady=(6, 6), sticky="ew")

        # Distribute buttons evenly
        for col in range(3):
            bar.grid_columnconfigure(col, weight=1)

        btn_cfg = dict(
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=42,
            corner_radius=10,
        )

        self.complete_btn = ctk.CTkButton(
            bar,
            text="✔  Mark Complete",
            fg_color="#1f5c3a",
            hover_color="#2a7a4f",
            text_color=self.CLR_SUCCESS,
            command=self._on_complete,
            **btn_cfg,
        )
        self.complete_btn.grid(row=0, column=0, padx=(16, 6), pady=12, sticky="ew")

        self.delete_btn = ctk.CTkButton(
            bar,
            text="🗑  Delete Task",
            fg_color="#5c1f1f",
            hover_color="#7a2a2a",
            text_color=self.CLR_ACCENT2,
            command=self._on_delete,
            **btn_cfg,
        )
        self.delete_btn.grid(row=0, column=1, padx=6, pady=12, sticky="ew")

        self.clear_btn = ctk.CTkButton(
            bar,
            text="⚠  Clear All",
            fg_color="#3a3a1f",
            hover_color="#5a5a2a",
            text_color=self.CLR_WARN,
            command=self._on_clear_all,
            **btn_cfg,
        )
        self.clear_btn.grid(row=0, column=2, padx=(6, 16), pady=12, sticky="ew")

    def _build_status_bar(self):
        """Bottom status bar for feedback messages."""
        self.status_var = ctk.StringVar(value="Ready — Load a task to get started.")
        status = ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.CLR_MUTED,
            anchor="w",
        )
        status.grid(row=4, column=0, padx=26, pady=(2, 10), sticky="ew")

    # ── Task Card Rendering ─────────────────────────────────────────────

    def display_tasks(self) -> None:
        """
        OUTPUT function — rebuild the visual task list from `tasks`.
        Clears old cards and renders fresh ones for every task.
        """
        # Destroy existing cards
        for card in self._task_cards:
            card.destroy()
        self._task_cards.clear()
        self._selected_task_id = None

        # Update counter
        total     = len(tasks)
        done      = sum(1 for t in tasks if t["completed"])
        pending   = total - done
        self.counter_label.configure(
            text=f"{total} task{'s' if total != 1 else ''}  |  "
                 f"✔ {done} done  |  ⏳ {pending} pending"
        )

        if not tasks:
            self.placeholder_label.grid(row=0, column=0, padx=20, pady=40)
            return

        self.placeholder_label.grid_forget()

        for idx, task in enumerate(tasks):
            self._render_task_card(idx, task)

    def _render_task_card(self, row_idx: int, task: dict) -> None:
        """Build a single task card widget and bind click-to-select."""
        is_done    = task["completed"]
        bg_color   = self.CLR_DONE_BG if is_done else "#1e2130"
        name_color = self.CLR_DONE_TEXT if is_done else self.CLR_TEXT
        id_color   = self.CLR_MUTED

        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=bg_color,
            corner_radius=10,
            border_width=1,
            border_color="#2a2d3e",
        )
        card.grid(row=row_idx, column=0, padx=10, pady=5, sticky="ew")
        card.grid_columnconfigure(1, weight=1)
        card.task_id = task["id"]   # Attach ID for selection tracking

        # Status icon
        icon_text  = "✔" if is_done else "○"
        icon_color = self.CLR_SUCCESS if is_done else self.CLR_MUTED
        icon = ctk.CTkLabel(
            card,
            text=icon_text,
            font=ctk.CTkFont(family="Segoe UI", size=18),
            text_color=icon_color,
            width=36,
        )
        icon.grid(row=0, column=0, rowspan=2, padx=(14, 8), pady=12)

        # Task name
        name_label = ctk.CTkLabel(
            card,
            text=("✔ " if is_done else "") + task["task_name"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
                weight="bold" if not is_done else "normal",
            ),
            text_color=name_color,
            anchor="w",
            wraplength=500,
        )
        name_label.grid(row=0, column=1, padx=(0, 10), pady=(10, 2), sticky="ew")

        # ID sub-label
        id_label = ctk.CTkLabel(
            card,
            text=f"ID #{task['id']}",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=id_color,
            anchor="w",
        )
        id_label.grid(row=1, column=1, padx=(0, 10), pady=(0, 10), sticky="w")

        # Status badge
        badge_text  = "Completed" if is_done else "Pending"
        badge_color = self.CLR_DONE_BG if is_done else "#1e2545"
        badge_fg    = self.CLR_SUCCESS  if is_done else "#7ca9e0"
        badge = ctk.CTkLabel(
            card,
            text=badge_text,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=badge_fg,
            fg_color=badge_color,
            corner_radius=6,
            padx=8, pady=2,
        )
        badge.grid(row=0, column=2, rowspan=2, padx=(0, 14), pady=12)

        # Bind click-to-select on all sub-widgets
        for widget in (card, icon, name_label, id_label, badge):
            widget.bind("<Button-1>", lambda e, c=card: self._select_card(c))

        self._task_cards.append(card)

    def _select_card(self, clicked_card: ctk.CTkFrame) -> None:
        """Highlight the clicked card and store the selected task ID."""
        for card in self._task_cards:
            is_selected = card is clicked_card
            task = next((t for t in tasks if t["id"] == card.task_id), None)
            if task:
                base_color = self.CLR_DONE_BG if task["completed"] else "#1e2130"
                card.configure(
                    fg_color=self.CLR_ACCENT if is_selected else base_color,
                    border_color=self.CLR_ACCENT if is_selected else "#2a2d3e",
                )

        self._selected_task_id = clicked_card.task_id
        task_name = next(
            (t["task_name"] for t in tasks if t["id"] == clicked_card.task_id), ""
        )
        self._set_status(f"Selected: {task_name[:60]}", color=self.CLR_ACCENT)

    # ── Button Handlers (Input → Process → Output) ──────────────────────

    def _on_add(self) -> None:
        """Handle Add Task button / Enter key."""
        raw_input = self.task_entry.get()              # INPUT
        success, msg = add_task(raw_input)             # PROCESS
        if success:
            self.task_entry.delete(0, "end")
            self.display_tasks()                       # OUTPUT
            self._set_status(msg, color=self.CLR_SUCCESS)
        else:
            self._set_status(msg, color=self.CLR_ACCENT2)
            self._shake_entry()

    def _on_complete(self) -> None:
        """Mark the selected task as completed."""
        if self._selected_task_id is None:
            self._set_status("Please select a task first.", color=self.CLR_WARN)
            return
        success, msg = mark_completed(self._selected_task_id)  # PROCESS
        self.display_tasks()                                    # OUTPUT
        color = self.CLR_SUCCESS if success else self.CLR_WARN
        self._set_status(msg, color=color)

    def _on_delete(self) -> None:
        """Delete the selected task after confirmation."""
        if self._selected_task_id is None:
            self._set_status("Please select a task first.", color=self.CLR_WARN)
            return
        task_name = next(
            (t["task_name"] for t in tasks if t["id"] == self._selected_task_id), "?"
        )
        confirm = messagebox.askyesno(
            "Delete Task",
            f'Are you sure you want to delete:\n\n"{task_name}"?',
        )
        if confirm:
            success, msg = delete_task(self._selected_task_id)   # PROCESS
            self.display_tasks()                                  # OUTPUT
            color = self.CLR_ACCENT2 if success else self.CLR_WARN
            self._set_status(msg, color=color)

    def _on_clear_all(self) -> None:
        """Clear every task after confirmation."""
        if not tasks:
            self._set_status("No tasks to clear.", color=self.CLR_WARN)
            return
        confirm = messagebox.askyesno(
            "Clear All Tasks",
            f"This will permanently delete all {len(tasks)} task(s).\n\nContinue?",
        )
        if confirm:
            success, msg = clear_all_tasks()   # PROCESS
            self.display_tasks()               # OUTPUT
            color = self.CLR_WARN if success else self.CLR_MUTED
            self._set_status(msg, color=color)

    # ── Helpers ─────────────────────────────────────────────────────────

    def _set_status(self, message: str, color: str = "#8892a4") -> None:
        """Update the bottom status bar."""
        self.status_var.set(f"  ›  {message}")
        self.status_bar_label_ref = self.nametowidget(
            self.winfo_children()[-1].winfo_name()  # status label is last child
        )
        # Find the actual status label and recolor it
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("textvariable") == self.status_var:  # noqa: E501
                widget.configure(text_color=color)
                break

    def _shake_entry(self) -> None:
        """Brief red-flash animation on the entry for invalid input."""
        original = self.task_entry.cget("border_color")
        self.task_entry.configure(border_color=self.CLR_ACCENT2)
        self.after(500, lambda: self.task_entry.configure(border_color=original))


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = ToDoApp()
    app.mainloop()
