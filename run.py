import subprocess
import sys
import os

def main():
    print("======================================================================")
    print("           Starting AuraSMS Premium Platform (FastAPI + SPA)           ")
    print("======================================================================")
    
    # Absolute path to backend directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "backend")
    
    # Path to venv python executable
    if sys.platform == "win32":
        python_exe = os.path.join(backend_dir, "venv", "Scripts", "python.exe")
    else:
        python_exe = os.path.join(backend_dir, "venv", "bin", "python")
        
    if not os.path.exists(python_exe):
        print(f"Error: Python executable not found at {python_exe}.")
        print("Please ensure the virtual environment is set up and requirements are installed.")
        sys.exit(1)
        
    print(f"Using virtual environment Python at: {python_exe}")
    print("Serving API and Static Frontend together on: http://127.0.0.1:8000")
    print("API Documentation available at: http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to terminate...")
    
    try:
        # Run uvicorn in the backend folder so 'app.main:app' can be imported correctly
        subprocess.run([python_exe, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"], cwd=backend_dir)
    except KeyboardInterrupt:
        print("\nShutdown signal received. Exiting AuraSMS.")
        
if __name__ == "__main__":
    main()
