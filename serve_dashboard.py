import os
import sys
import webbrowser
import http.server
import socketserver
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from export_data import export_data


def start_server(port=8080):
    os.chdir("web")

    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Dashboard running at http://localhost:{port}")
        httpd.serve_forever()


def auto_refresh(interval=30):
    while True:
        time.sleep(interval)
        try:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            export_data()
            os.chdir("web")
        except Exception:
            pass


if __name__ == "__main__":
    port = 8080

    print("Updating data...")
    export_data()

    print(f"Starting dashboard server on port {port}...")
    refresh_thread = threading.Thread(target=auto_refresh, args=(30,), daemon=True)
    refresh_thread.start()

    webbrowser.open(f"http://localhost:{port}")
    start_server(port)
