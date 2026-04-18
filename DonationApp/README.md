# DonationApp — Local setup

Steps to configure a Python environment and install dependencies (Windows):

1. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
python app.py
```

4. In VS Code, select the Python interpreter from the `venv\Scripts\python.exe` environment. Installing the packages above will allow Pylance to resolve `flask` and `flask_login` imports.
