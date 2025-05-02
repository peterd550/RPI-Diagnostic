import os
import time
import shutil
import subprocess
import psutil
import platform
import socket
import webbrowser
from datetime import datetime
import getpass

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

def check_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "Unavailable"

def check_sudo_user():
    return getpass.getuser()

def check_ssh():
    try:
        with open("/etc/ssh/sshd_config", "r") as f:
            lines = f.readlines()
        return "Enabled" if any("PermitRootLogin" in line or "PasswordAuthentication" in line for line in lines) else "Unknown"
    except:
        return "Unavailable"

def check_updates():
    try:
        output = subprocess.check_output("apt list --upgradable 2>/dev/null", shell=True).decode()
        lines = [line for line in output.splitlines() if not line.startswith("Listing")]
        return f"{len(lines)} packages available" if lines else "Up to date"
    except:
        return "Unavailable"

def check_usb_devices():
    try:
        output = subprocess.check_output("lsusb", shell=True).decode()
        devices = output.strip().splitlines()
        return f"{len(devices)} device(s): " + ", ".join([d.split()[-1] for d in devices])
    except:
        return "Unavailable"

def check_hostname():
    try:
        return socket.gethostname()
    except:
        return "Unavailable"

def check_ping():
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return "Success"
    except Exception:
        return "Failed"

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

    print(f"\n✅ HTML report saved to: {report_filename}")
    webbrowser.get("chromium-browser").open(f"file://{os.path.abspath(report_filename)}")

# ------------- Main Diagnostic Runner -------------

def run_diagnostics():
    results = []
    results.append(f"<tr><td>CPU Usage</td><td>{check_cpu()}</td></tr>")
    results.append(f"<tr><td>RAM Usage</td><td>{check_ram()}</td></tr>")
    results.append(f"<tr><td>WiFi Status</td><td>{check_wifi()}</td></tr>")
    results.append(f"<tr><td>Disk Usage</td><td>{check_disk()}</td></tr>")
    results.append(f"<tr><td>CPU Temperature</td><td>{check_temp()}</td></tr>")
    results.append(f"<tr><td>Ping Connectivity</td><td>{check_ping()}</td></tr>")
    results.append(f"<tr><td>IP Address</td><td>{check_ip()}</td></tr>")
    results.append(f"<tr><td>Sudo User</td><td>{check_sudo_user()}</td></tr>")
    results.append(f"<tr><td>SSH Config</td><td>{check_ssh()}</td></tr>")
    results.append(f"<tr><td>Available Updates</td><td>{check_updates()}</td></tr>")
    results.append(f"<tr><td>USB Devices</td><td>{check_usb_devices()}</td></tr>")
    results.append(f"<tr><td>Pi Hostname</td><td>{check_hostname()}</td></tr>")

    generate_html_report(results)

# ------------- Entry Point -------------

if __name__ == "__main__":
    run_diagnostics()
