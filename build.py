"""
Automated PyInstaller Build Script
Builds a standalone executable for Windows/Linux/Mac.
"""

import os
import sys
import subprocess
import shutil

def build():
    print("==================================================")
    print("Building Standalone PPTX Translator Executable...")
    print("==================================================")

    project_root = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_root, "dist")
    build_dir = os.path.join(project_root, "build")

    # Clean old builds
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir, ignore_errors=True)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir, ignore_errors=True)

    # Assets to bundle
    dict_src = os.path.join(project_root, "src", "dictionaries")
    add_data_sep = ";" if sys.platform == "win32" else ":"
    data_arg = f"{dict_src}{add_data_sep}src/dictionaries"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "PPTX_Instruction_Translator",
        "--add-data", data_arg,
        os.path.join(project_root, "main.py")
    ]

    print(f"Executing: {' '.join(cmd)}\n")
    ret = subprocess.call(cmd)

    if ret == 0:
        print("\n==================================================")
        print("BUILD SUCCESSFUL!")
        print(f"Executable output: {os.path.join(dist_dir, 'PPTX_Instruction_Translator')}")
        print("==================================================")
    else:
        print("\n[!] Build failed with exit code:", ret)

if __name__ == "__main__":
    build()
