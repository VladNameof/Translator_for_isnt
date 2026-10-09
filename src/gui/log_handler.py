"""
Thread-safe Log Handler for GUI components.
"""

import tkinter as tk
import threading
from typing import Optional

class GUILogHandler:
    def __init__(self, text_widget: tk.Text):
        self.text_widget = text_widget
        self._lock = threading.Lock()

    def log(self, message: str, tag: Optional[str] = None):
        with self._lock:
            def _insert():
                self.text_widget.insert(tk.END, message + "\n", tag)
                self.text_widget.see(tk.END)
            self.text_widget.after(0, _insert)

    def clear(self):
        with self._lock:
            def _clear():
                self.text_widget.delete("1.0", tk.END)
            self.text_widget.after(0, _clear)
