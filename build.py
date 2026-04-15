import os
import platform
import subprocess

def build_app():
    print("Building INTELLI...")
    
    # Base pyinstaller command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--add-data", f"www{os.pathsep}www",
        "--add-data", f".env{os.pathsep}.",
        "--add-data", f"INTELLI.db{os.pathsep}.",
        "--name", "INTELLI",
        "run.py"
    ]
    
    if platform.system().lower() == "windows":
        cmd.append("--icon=www/assets/img/iNTELLI AI.ico")
    
    subprocess.run(cmd, check=True)
    print("Build complete! Check the 'dist' folder.")

if __name__ == "__main__":
    build_app()
