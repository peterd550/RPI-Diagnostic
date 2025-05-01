import os
import time
import shutil
import subprocess
import psutil
import platform
import socket
import webbrowser
from datetime import datetime

# ------------- Diagnostic Functions -------------

def check_cpu():
    return f"{psutil.cpu_percent()}% used"

def check_ram():
    mem = psutil.virtual_memory()
    return f"{mem.percent}% used ({mem.used // (1024 ** 2)}MB / {mem.total // (1024 ** 2)}MB)"

def check_wifi():
    try:
        result = subprocess.check_output("iwconfig 2>/dev/null", shell=True).decode()
        if "Link Quality" in result:
            return "Connected"
        else:
            return "Not Connected"
    except Exception as e:
        return f"Error: {e}"

def check_disk():
    usage = shutil.disk_usage("/")
    percent = (usage.used / usage.total) * 100
    return f"{percent:.2f}% used ({usage.used // (1024 ** 3)}GB / {usage.total // (1024 ** 3)}GB)"

def check_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_c = int(f.read()) / 1000.0
        return f"{temp_c:.1f} °C"
    except:
        return "Unavailable"

# ------------- Stress Test Function -------------

def stress_test():
    print("\nRunning CPU stress test for 120 seconds...")
    try:
        subprocess.run(
            ["stress", "--cpu", "4", "--timeout", "120s"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        )
        print("✅ Stress test completed\n")
    except FileNotFoundError:
        print("❌ 'stress' is not installed. Install it using: sudo apt install stress")

# ------------- HTML Report Generator -------------

def generate_html_report(results):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    report_filename = f"rpi_report_{timestamp}.html"

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial; background-color: white; color: black; text-align: center; }}
            table {{ border-collapse: collapse; width: 80%; margin: 20px auto; }}
            th, td {{ padding: 10px; border: 1px solid #ccc; }}
            th {{ background-color: #4CAF50; color: white; }}
        </style>
    </head>
    <body>
        <h2>Raspberry Pi Diagnostic Report</h2>
        <p>Generated: {datetime.now()}</p>
        <table>
            <tr><th>Test</th><th>Result</th></tr>
            {''.join(results)}
        </table>
    </body>
    </html>
    """

    with open(report_filename, "w") as f:
        f.write(html)

    print(f"✅ HTML report saved to: {report_filename}")
    webbrowser.get(using='chromium-browser').open(f"file://{os.path.abspath(report_filename)}")

# ------------- Main Diagnostic Runner -------------

def run_diagnostics():
    results = []
    results.append(f"<tr><td>CPU</td><td>{check_cpu()}</td></tr>")
    results.append(f"<tr><td>RAM</td><td>{check_ram()}</td></tr>")
    results.append(f"<tr><td>WiFi</td><td>{check_wifi()}</td></tr>")
    results.append(f"<tr><td>Disk</td><td>{check_disk()}</td></tr>")
    results.append(f"<tr><td>Temperature</td><td>{check_temp()}</td></tr>")

    stress_test()
    generate_html_report(results)

# ------------- Entry Point -------------

if __name__ == "__main__":
    run_diagnostics()
