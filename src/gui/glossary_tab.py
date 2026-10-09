"""
Glossary Tab Widget for GUI
Allows inspecting, searching, adding, and saving translation terms.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.core.glossary_manager import GlossaryManager

class GlossaryEditorTab(ttk.Frame):
    def __init__(self, parent, glossary_ua: GlossaryManager, glossary_en: GlossaryManager):
        super().__init__(parent)
        self.glossary_ua = glossary_ua
        self.glossary_en = glossary_en
        self.active_glossary = self.glossary_ua
        self.current_lang = "UA"

        self._build_ui()
        self.refresh_table()

    def _build_ui(self):
        # Top toolbar
        toolbar = ttk.Frame(self, padding=5)
        toolbar.pack(fill="x", side="top")

        ttk.Label(toolbar, text="Язык словаря:").pack(side="left", padx=5)
        self.combo_lang = ttk.Combobox(toolbar, values=["Ukrainian (UA)", "English (EN)"], state="readonly", width=15)
        self.combo_lang.set("Ukrainian (UA)")
        self.combo_lang.bind("<<ComboboxSelected>>", self._on_lang_changed)
        self.combo_lang.pack(side="left", padx=5)

        ttk.Label(toolbar, text="Поиск:").pack(side="left", padx=(15, 5))
        self.entry_search = ttk.Entry(toolbar, width=25)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<KeyRelease>", lambda e: self.refresh_table())

        btn_save = ttk.Button(toolbar, text="Сохранить словарь", command=self._save_active_dict)
        btn_save.pack(side="right", padx=5)

        btn_import = ttk.Button(toolbar, text="Импорт JSON...", command=self._import_json)
        btn_import.pack(side="right", padx=5)

        # Table View
        columns = ("source", "translation")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("source", text="Исходный текст (Source PL)")
        self.tree.heading("translation", text="Перевод (Target Translation)")
        self.tree.column("source", width=350, stretch=True)
        self.tree.column("translation", width=350, stretch=True)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(fill="both", expand=True, side="top", padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Bottom Add/Edit Frame
        edit_frame = ttk.LabelFrame(self, text="Добавить / Изменить термин", padding=5)
        edit_frame.pack(fill="x", side="bottom", padx=5, pady=5)

        ttk.Label(edit_frame, text="Исходный текст:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.entry_src = ttk.Entry(edit_frame, width=40)
        self.entry_src.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(edit_frame, text="Перевод:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.entry_dst = ttk.Entry(edit_frame, width=40)
        self.entry_dst.grid(row=0, column=3, sticky="ew", padx=5, pady=2)

        btn_add = ttk.Button(edit_frame, text="Сохранить термин", command=self._add_term)
        btn_add.grid(row=0, column=4, padx=10, pady=2)

        edit_frame.columnconfigure(1, weight=1)
        edit_frame.columnconfigure(3, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self._on_row_selected)

    def _on_lang_changed(self, event=None):
        val = self.combo_lang.get()
        if "UA" in val:
            self.active_glossary = self.glossary_ua
            self.current_lang = "UA"
        else:
            self.active_glossary = self.glossary_en
            self.current_lang = "EN"
        self.refresh_table()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = self.entry_search.get().lower().strip()
        for src, dst in self.active_glossary.direct_map.items():
            if query and (query not in src.lower() and query not in dst.lower()):
                continue
            self.tree.insert("", "end", values=(src, dst))

    def _on_row_selected(self, event=None):
        selected = self.tree.selection()
        if selected:
            vals = self.tree.item(selected[0], "values")
            if vals:
                self.entry_src.delete(0, tk.END)
                self.entry_src.insert(0, vals[0])
                self.entry_dst.delete(0, tk.END)
                self.entry_dst.insert(0, vals[1])

    def _add_term(self):
        src = self.entry_src.get().strip()
        dst = self.entry_dst.get().strip()
        if not src or not dst:
            messagebox.showwarning("Внимание", "Поля 'Исходный текст' и 'Перевод' не могут быть пустыми!")
            return
        self.active_glossary.add_entry(src, dst)
        self.refresh_table()
        messagebox.showinfo("Успех", f"Термин успешно сохранен в словарь {self.current_lang}!")

    def _save_active_dict(self):
        try:
            self.active_glossary.save_to_file()
            messagebox.showinfo("Успех", f"Словарь {self.current_lang} успешно сохранен на диск!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить словарь: {e}")

    def _import_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            try:
                self.active_glossary.load_from_file(file_path)
                self.refresh_table()
                messagebox.showinfo("Успех", f"Словарь успешно импортирован из {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка импорта: {e}")
