"""
Main Application Window for PPTX Manufacturing Instruction Translator
Supports batch file translation, progress tracking, live logging, and QA verification.
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.core.glossary_manager import GlossaryManager
from src.core.engine import PPTXTranslationEngine
from src.core.verifier import PPTXVerifier
from src.gui.log_handler import GUILogHandler
from src.gui.glossary_tab import GlossaryEditorTab

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PPTX Instruction Translator (Zoid Rack / MPI / FlexFlow)")
        self.geometry("900x650")
        self.minsize(800, 550)

        # Initialize Glossaries
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.glossary_ua = GlossaryManager.create_for_language("ua", base_dir)
        self.glossary_en = GlossaryManager.create_for_language("en", base_dir)

        # State Variables
        self.src_folder = tk.StringVar(value=os.getcwd())
        self.translate_ua = tk.BooleanVar(value=True)
        self.translate_en = tk.BooleanVar(value=True)
        self.auto_verify = tk.BooleanVar(value=True)
        self.is_processing = False

        self._setup_styles()
        self._build_ui()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=5)
        style.configure("Primary.TButton", font=("Segoe UI", 11, "bold"), background="#0078D7", foreground="white")
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        # Tab Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Translation Dashboard
        tab_main = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_main, text="Перевод файлов (Dashboard)")
        self._build_dashboard_tab(tab_main)

        # Tab 2: Glossary & Terms Editor
        tab_glossary = GlossaryEditorTab(self.notebook, self.glossary_ua, self.glossary_en)
        self.notebook.add(tab_glossary, text="Редактор словарей (Glossary)")

    def _build_dashboard_tab(self, parent):
        # 1. Folder Selection Frame
        frame_dir = ttk.LabelFrame(parent, text="Папка с исходными файлами (.pptx)", padding=10)
        frame_dir.pack(fill="x", side="top", pady=(0, 10))

        entry_dir = ttk.Entry(frame_dir, textvariable=self.src_folder, font=("Segoe UI", 10))
        entry_dir.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_browse = ttk.Button(frame_dir, text="Выбрать...", command=self._browse_folder, width=12)
        btn_browse.pack(side="right")

        # 2. Options & Targets
        frame_opts = ttk.LabelFrame(parent, text="Параметры генерации и языки", padding=10)
        frame_opts.pack(fill="x", side="top", pady=(0, 10))

        chk_ua = ttk.Checkbutton(frame_opts, text="Украинский перевод (UA) -> папка translated_UA", variable=self.translate_ua)
        chk_ua.pack(anchor="w", pady=2)

        chk_en = ttk.Checkbutton(frame_opts, text="Английский перевод (EN) -> папка translated_EN", variable=self.translate_en)
        chk_en.pack(anchor="w", pady=2)

        chk_ver = ttk.Checkbutton(frame_opts, text="Автоматическая верификация после перевода (проверка на 0% остатков)", variable=self.auto_verify)
        chk_ver.pack(anchor="w", pady=2)

        # 3. Action Buttons & Progress
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill="x", side="top", pady=(0, 10))

        self.btn_run = ttk.Button(action_frame, text="▶ Запустить перевод", command=self._start_translation_thread, style="Primary.TButton")
        self.btn_run.pack(fill="x", ipady=5)

        self.progress_bar = ttk.Progressbar(action_frame, mode="indeterminate")
        self.progress_bar.pack(fill="x", pady=(5, 0))

        # 4. Real-time Output Log
        frame_log = ttk.LabelFrame(parent, text="Лог выполнения процесса", padding=10)
        frame_log.pack(fill="both", expand=True, side="bottom")

        self.txt_log = tk.Text(frame_log, wrap="word", font=("Consolas", 9), bg="#1E1E1E", fg="#D4D4D4", insertbackground="white")
        self.txt_log.pack(fill="both", expand=True, side="left")

        scroll = ttk.Scrollbar(frame_log, orient="vertical", command=self.txt_log.yview)
        scroll.pack(side="right", fill="y")
        self.txt_log.configure(yscrollcommand=scroll.set)

        self.txt_log.tag_config("pass", foreground="#4EC9B0")
        self.txt_log.tag_config("fail", foreground="#F14C4C")
        self.txt_log.tag_config("info", foreground="#9CDCFE")
        self.txt_log.tag_config("header", foreground="#DCDCAA", font=("Consolas", 10, "bold"))

        self.logger = GUILogHandler(self.txt_log)

    def _browse_folder(self):
        d = filedialog.askdirectory(initialdir=self.src_folder.get())
        if d:
            self.src_folder.set(d)

    def _start_translation_thread(self):
        if self.is_processing:
            return
        
        src = self.src_folder.get().strip()
        if not src or not os.path.isdir(src):
            messagebox.showerror("Ошибка", "Пожалуйста, выберите корректную папку!")
            return

        if not self.translate_ua.get() and not self.translate_en.get():
            messagebox.showwarning("Внимание", "Выберите хотя бы один целевой язык (UA или EN)!")
            return

        self.is_processing = True
        self.btn_run.configure(state="disabled")
        self.progress_bar.start(10)
        self.logger.clear()

        thread = threading.Thread(target=self._run_translation_worker, daemon=True)
        thread.start()

    def _run_translation_worker(self):
        try:
            src_dir = self.src_folder.get().strip()
            files = [
                f for f in os.listdir(src_dir)
                if f.lower().endswith(".pptx")
                and not f.startswith("~")
                and not f.startswith("translated_")
            ]

            if not files:
                self.logger.log("[!] В выбранной папке не найдено файлов презентаций .pptx", "fail")
                return

            self.logger.log(f"==================================================", "header")
            self.logger.log(f"Найдено файлов для перевода: {len(files)}", "info")
            self.logger.log(f"Рабочая папка: {src_dir}\n", "info")

            engine_ua = PPTXTranslationEngine(self.glossary_ua)
            engine_en = PPTXTranslationEngine(self.glossary_en)
            verifier = PPTXVerifier()

            ua_dir = os.path.join(src_dir, "translated_UA")
            en_dir = os.path.join(src_dir, "translated_EN")

            for idx, f in enumerate(files, start=1):
                full_src = os.path.join(src_dir, f)
                self.logger.log(f"[{idx}/{len(files)}] Обработка: {f}", "header")

                # Format Output File Names
                base_name = f[:-5]
                clean_base = base_name[:-3].strip() if base_name.endswith(" PL") else base_name

                # 1. Ukrainian Translation
                if self.translate_ua.get():
                    ua_name = f"{clean_base} UA.pptx"
                    ua_target = os.path.join(ua_dir, ua_name)
                    res_ua = engine_ua.translate_presentation(full_src, ua_target)
                    self.logger.log(f"  [UA] Переведено блоков: {res_ua.translated_count} -> {ua_name}", "info")

                    if self.auto_verify.get():
                        v_res = verifier.verify_file(ua_target)
                        if v_res.is_passed:
                            self.logger.log(f"  [UA PASS] Верификация успешна: 0 польских остатков ({v_res.total_text_nodes} нод)", "pass")
                        else:
                            self.logger.log(f"  [UA FAIL] Обнаружены непереведенные слова ({len(v_res.issues)}):", "fail")
                            for iss in v_res.issues[:5]:
                                self.logger.log(f"    - Слайд {iss.slide} [{iss.matched_keyword}]: {iss.text}", "fail")

                # 2. English Translation
                if self.translate_en.get():
                    en_name = f"{clean_base} EN.pptx"
                    en_target = os.path.join(en_dir, en_name)
                    res_en = engine_en.translate_presentation(full_src, en_target)
                    self.logger.log(f"  [EN] Переведено блоков: {res_en.translated_count} -> {en_name}", "info")

                    if self.auto_verify.get():
                        v_res = verifier.verify_file(en_target)
                        if v_res.is_passed:
                            self.logger.log(f"  [EN PASS] Верификация успешна: 0 польских остатков ({v_res.total_text_nodes} нод)", "pass")
                        else:
                            self.logger.log(f"  [EN FAIL] Обнаружены непереведенные слова ({len(v_res.issues)}):", "fail")
                            for iss in v_res.issues[:5]:
                                self.logger.log(f"    - Слайд {iss.slide} [{iss.matched_keyword}]: {iss.text}", "fail")

            self.logger.log(f"\n==================================================", "header")
            self.logger.log(f"ПЕРЕВОД И ПРОВЕРКА ВСЕХ ФАЙЛОВ УСПЕШНО ЗАВЕРШЕНЫ!", "pass")

        except Exception as e:
            self.logger.log(f"\n[ERROR] Ошибка выполнения: {str(e)}", "fail")
            messagebox.showerror("Ошибка", f"Произошла ошибка при переводе:\n{e}")
        finally:
            self.progress_bar.stop()
            self.btn_run.configure(state="normal")
            self.is_processing = False
