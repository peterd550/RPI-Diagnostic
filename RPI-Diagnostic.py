import os
import time
import shutil
import subprocess
import psutil
import platform
import socket
import webbrowser
import threading
from datetime import datetime
import matplotlib.pyplot as plt

# ------------- CPU Load Simulation (Stress Replacement) -------------

def simulate_cpu_load(duration=60):
    print(f"\n⚙️ Simulating CPU load for {duration} seconds...")
    end_time = time.time() + duration

    def cpu_task():
        while time.time() < end_time:
            _ = 3.1415 ** 2.7182

    threads = []
    for _ in range(psutil.cpu_count()):
        t = threading.Thread(target=cpu_task)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("✅ CPU load simulation completed.\n")

# ------------- Diagnostic Functions -------------

def check_cpu():
    return f"{psutil.cpu_percent()}% used"

def check_ram():
    mem = psutil.virtual_memory()
    return f"{mem.percent}% used ({mem.used // (1024 ** 2)}MB / {mem.total // (1024 ** 2)}MB)"

def check_wifi():
    try:
        result = subprocess.check_output("iwconfig 2>/dev/null", shell=True).decode()
        return "Connected" if "Link Quality" in result else "Not Connected"
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

def check_hostname():
    return socket.gethostname()

def check_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "Unavailable"

def check_sudo_user():
    return os.getenv("SUDO_USER") or "Not run with sudo"

def check_ssh_config():
    return "Enabled" if os.path.exists("/etc/ssh/sshd_config") else "Disabled"

def check_updates():
    try:
        subprocess.run("sudo apt update > /dev/null", shell=True)
        output = subprocess.check_output("apt list --upgradable 2>/dev/null | wc -l", shell=True).decode().strip()
        count = int(output) - 1 if output.isdigit() else 0
        return f"{count} packages upgradable"
    except:
        return "Error checking updates"

def check_usb_devices():
    try:
        output = subprocess.check_output("lsusb", shell=True).decode()
        return output.replace("\n", ", ")
    except:
        return "Error detecting USB devices"

# ------------- Live Data Graph -------------

def generate_graph():
    print("📈 Generating CPU usage and temperature graph...")
    cpu_data = []
    temp_data = []
    timestamps = []

    for i in range(30):
        cpu_data.append(psutil.cpu_percent())
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp_c = int(f.read()) / 1000.0
            temp_data.append(temp_c)
        except:
            temp_data.append(None)
        timestamps.append(i)
        time.sleep(1)

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, cpu_data, label="CPU Usage (%)", color="blue")
    plt.plot(timestamps, temp_data, label="CPU Temp (°C)", color="red")
    plt.xlabel("Time (s)")
    plt.ylabel("Value")
    plt.title("CPU Usage and Temperature Over Time")
    plt.legend()
    plt.tight_layout()
    plt.savefig("cpu_temp_chart.png")
    print("✅ Graph saved as cpu_temp_chart.png")

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
            img {{ margin-top: 20px; max-width: 80%; }}
        </style>
    </head>
    <body>
        <h2>Raspberry Pi Diagnostic Report</h2>
        <p>Generated: {datetime.now()}</p>
        <table>
            <tr><th>Test</th><th>Result</th></tr>
            {''.join(results)}
        </table>
        <img src='cpu_temp_chart.png' alt='CPU Chart'>
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
    results.append(f"<tr><td>Hostname</td><td>{check_hostname()}</td></tr>")
    results.append(f"<tr><td>IP Address</td><td>{check_ip()}</td></tr>")
    results.append(f"<tr><td>Sudo User</td><td>{check_sudo_user()}</td></tr>")
    results.append(f"<tr><td>SSH Config</td><td>{check_ssh_config()}</td></tr>")
    results.append(f"<tr><td>Available Updates</td><td>{check_updates()}</td></tr>")
    results.append(f"<tr><td>USB Devices</td><td>{check_usb_devices()}</td></tr>")
    results.append(f"<tr><td>CPU</td><td>{check_cpu()}</td></tr>")
    results.append(f"<tr><td>RAM</td><td>{check_ram()}</td></tr>")
    results.append(f"<tr><td>WiFi</td><td>{check_wifi()}</td></tr>")
    results.append(f"<tr><td>Disk</td><td>{check_disk()}</td></tr>")
    results.append(f"<tr><td>Temperature</td><td>{check_temp()}</td></tr>")

    simulate_cpu_load()
    generate_graph()
    generate_html_report(results)

# ------------- Entry Point -------------

if __name__ == "__main__":
    run_diagnostics()
