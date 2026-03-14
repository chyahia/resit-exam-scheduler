import os
import sys
import time
import webbrowser
import threading
import streamlit.web.cli as stcli

def open_browser():
    time.sleep(3)
    webbrowser.open_new("http://localhost:8501")

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    app_path = os.path.join(base_path, 'app.py')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 🌟 السر هنا: إجبار Streamlit على إيقاف وضع التطوير وتحديد المنفذ بدقة 🌟
    sys.argv = [
        "streamlit", 
        "run", 
        app_path, 
        "--server.port=8501", 
        "--server.headless=true", 
        "--global.developmentMode=false"
    ]
    sys.exit(stcli.main())