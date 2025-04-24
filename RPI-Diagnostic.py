import os
import platform
import psutil
import socket
import subprocess
from datetime import datetime, timedelta
from tkinter import filedialog, Tk

# Emoji and color setup
TICK = "✅"
CROSS = "❌"

# Log and HTML buffer
log_lines = []
html_rows = []

def log_result(label, value, passed=True):
    symbol = TICK if passed else CROSS
    line = f"{label}: {symbol} {value}"
    log_lines.append(line)

    html_color = "green" if passed else "red"
    html_rows.append(f"<tr><td>{label}</td><td style='color:{html_color}'>{symbol} {value}</td></tr>")

def run_command(cmd):
    try:
        return subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        return "Unavailable"

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return int(f.read()) / 1000.0
    except:
        return None

def check_cpu_temp():
    temp = get_cpu_temp()
    if temp is None:
        log_result("CPU Temperature", "Unavailable", False)
    elif temp < 75:
        log_result("CPU Temperature", f"{temp:.2f}°C", True)
    else:
        log_result("CPU Temperature", f"{temp:.2f}°C (Too hot)", False)

def check_usage(label, percent):
    log_result(f"{label} Usage", f"{percent:.2f}%", percent < 85)

def check_ip():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        log_result("IP Address", ip, True)
    except:
        log_result("IP Address", "Unavailable", False)

def check_throttling():
    code = run_command("vcgencmd get_throttled").split("=")[-1]
    if code == "0x0":
        log_result("Throttling", f"Code: {code} (No throttling)", True)
    else:
        log_result("Throttling", f"Code: {code} (Issues detected)", False)

def check_command(label, cmd):
    result = run_command(cmd)
    log_result(label, result, "Unavailable" not in result)

def run_diagnostics():
    log_result("System", f"{platform.system()} {platform.release()}")
    log_result("Architecture", platform.machine())
    check_command("Model", "cat /proc/device-tree/model")
    log_result("Uptime", str(timedelta(seconds=int((datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds()))))

    check_cpu_temp()
    check_usage("CPU", psutil.cpu_percent())
    check_usage("Memory", psutil.virtual_memory().percent)
    check_usage("Disk", psutil.disk_usage('/').percent)
    check_ip()
    check_throttling()

    check_command("Voltage", "vcgencmd measure_volts")
    check_command("GPU Memory", "vcgencmd get_mem gpu")
    check_command("ARM Frequency", "vcgencmd measure_clock arm")

def save_log_file(path="diagnostic.log"):
    with open(path, "a") as f:
        f.write(f"\n===== Diagnostic Run at {datetime.now()} =====\n")
        for line in log_lines:
            f.write(line + "\n")

def generate_html_report(path):
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial; background-color: #f5f5f5; color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #4CAF50; color: white; }}
        </style>
    </head>
    <body>
        <h2>Raspberry Pi Diagnostic Report</h2>
        <p>Generated: {datetime.now()}</p>
        <table>
            <tr><th>Test</th><th>Result</th></tr>
            {''.join(html_rows)}
        </table>
    </body>
    </html>
    """
    with open(path, "w") as f:
        f.write(html)

def save_html_with_popup():
    Tk().withdraw()  # Hide root window
    path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML files", "*.html")])
    if path:
        generate_html_report(path)
        print(f"✅ HTML report saved to {path}")
    else:
        print("❌ Report save cancelled.")

if __name__ == "__main__":
    run_diagnostics()
    save_log_file()  # Default log file
    save_html_with_popup()
