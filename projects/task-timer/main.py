import tkinter as tk
from tkinter import messagebox


DEFAULT_DURATION_SECONDS = 25 * 60


class TaskTimerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Task Timer")
        self.root.geometry("520x420")
        self.root.minsize(480, 380)

        self.tasks: list[dict[str, object]] = []
        self.current_task_index: int | None = None
        self.remaining_seconds = DEFAULT_DURATION_SECONDS
        self.timer_job: str | None = None
        self.is_running = False

        self._build_ui()
        self._update_timer_label()
        self._refresh_task_list()

    def _build_ui(self) -> None:
        container = tk.Frame(self.root, padx=12, pady=12)
        container.pack(fill="both", expand=True)

        input_frame = tk.Frame(container)
        input_frame.pack(fill="x", pady=(0, 10))

        self.task_entry = tk.Entry(input_frame)
        self.task_entry.pack(side="left", fill="x", expand=True)
        self.task_entry.bind("<Return>", lambda _event: self.add_task())

        add_button = tk.Button(input_frame, text="Add Task", width=12, command=self.add_task)
        add_button.pack(side="left", padx=(8, 0))

        list_frame = tk.Frame(container)
        list_frame.pack(fill="both", expand=True)

        self.task_listbox = tk.Listbox(list_frame, activestyle="dotbox")
        self.task_listbox.pack(side="left", fill="both", expand=True)
        self.task_listbox.bind("<<ListboxSelect>>", self.on_task_select)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.task_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.task_listbox.config(yscrollcommand=scrollbar.set)

        timer_frame = tk.Frame(container, pady=12)
        timer_frame.pack(fill="x")

        self.selected_task_var = tk.StringVar(value="Selected task: None")
        selected_task_label = tk.Label(
            timer_frame,
            textvariable=self.selected_task_var,
            anchor="w",
            font=("Arial", 11),
        )
        selected_task_label.pack(fill="x")

        self.timer_var = tk.StringVar(value="25:00")
        timer_label = tk.Label(
            timer_frame,
            textvariable=self.timer_var,
            font=("Arial", 28, "bold"),
            pady=8,
        )
        timer_label.pack()

        button_frame = tk.Frame(container)
        button_frame.pack(fill="x")

        tk.Button(button_frame, text="Start 25 min", width=14, command=self.start_timer).pack(
            side="left", padx=(0, 6)
        )
        tk.Button(button_frame, text="Stop", width=10, command=self.stop_timer).pack(
            side="left", padx=6
        )
        tk.Button(button_frame, text="Reset", width=10, command=self.reset_timer).pack(
            side="left", padx=6
        )
        tk.Button(
            button_frame, text="Mark Complete", width=14, command=self.mark_complete
        ).pack(side="right")

    def add_task(self) -> None:
        task_name = self.task_entry.get().strip()
        if not task_name:
            messagebox.showwarning("Input required", "Please enter a task.")
            return

        self.tasks.append(
            {
                "name": task_name,
                "completed": False,
            }
        )
        self.task_entry.delete(0, tk.END)
        self._refresh_task_list()

    def _refresh_task_list(self) -> None:
        current_selection = self.task_listbox.curselection()
        selected_index = current_selection[0] if current_selection else None

        self.task_listbox.delete(0, tk.END)
        for index, task in enumerate(self.tasks):
            prefix = "✓" if bool(task["completed"]) else "•"
            suffix = " (active)" if index == self.current_task_index and self.is_running else ""
            self.task_listbox.insert(tk.END, f"{prefix} {task['name']}{suffix}")

        if selected_index is not None and selected_index < len(self.tasks):
            self.task_listbox.selection_set(selected_index)

    def on_task_select(self, _event=None) -> None:
        selection = self.task_listbox.curselection()
        if not selection:
            self.selected_task_var.set("Selected task: None")
            return

        index = selection[0]
        task_name = str(self.tasks[index]["name"])
        self.selected_task_var.set(f"Selected task: {task_name}")

        if index != self.current_task_index and not self.is_running:
            self.current_task_index = index
            self.remaining_seconds = DEFAULT_DURATION_SECONDS
            self._update_timer_label()

    def start_timer(self) -> None:
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection required", "Please select a task first.")
            return

        selected_index = selection[0]

        if self.current_task_index != selected_index:
            self.current_task_index = selected_index
            self.remaining_seconds = DEFAULT_DURATION_SECONDS

        if self.remaining_seconds <= 0:
            self.remaining_seconds = DEFAULT_DURATION_SECONDS

        if not self.is_running:
            self.is_running = True
            self._refresh_task_list()
            self._tick()

    def stop_timer(self) -> None:
        self.is_running = False
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        self._refresh_task_list()

    def reset_timer(self) -> None:
        self.stop_timer()
        self.remaining_seconds = DEFAULT_DURATION_SECONDS
        self._update_timer_label()

    def mark_complete(self) -> None:
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection required", "Please select a task first.")
            return

        index = selection[0]
        self.tasks[index]["completed"] = True

        if self.current_task_index == index:
            self.stop_timer()
            self.remaining_seconds = DEFAULT_DURATION_SECONDS
            self._update_timer_label()

        self._refresh_task_list()

    def _tick(self) -> None:
        if not self.is_running:
            return

        self._update_timer_label()

        if self.remaining_seconds <= 0:
            self.is_running = False
            self.timer_job = None
            self._refresh_task_list()

            task_name = (
                str(self.tasks[self.current_task_index]["name"])
                if self.current_task_index is not None
                else "Task"
            )
            messagebox.showinfo("Timer finished", f"{task_name} timer is complete.")
            return

        self.remaining_seconds -= 1
        self.timer_job = self.root.after(1000, self._tick)

    def _update_timer_label(self) -> None:
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        self.timer_var.set(f"{minutes:02d}:{seconds:02d}")


def main() -> None:
    root = tk.Tk()
    TaskTimerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
