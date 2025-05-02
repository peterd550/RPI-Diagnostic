import os
import time
import shutil
import subprocess
import psutil
import platform
import socket
import webbrowser
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

# ----- Utility Functions -----

def run_command(command):
    return subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True).stdout.strip()

# ----- Diagnostics -----

def get_cpu_usage():
    return f"{psutil.cpu_percent()}%"

def get_ram_usage():
    mem = psutil.virtual_memory()
    return f"{mem.percent}% ({mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB)"

def get_disk_usage():
    partitions = psutil.disk_partitions()
    results = []
    for p in partitions:
        try:
            usage = psutil.disk_usage(p.mountpoint)
            results.append(f"{p.device} {p.mountpoint}: {usage.percent:.2f}% ({usage.used // (1024**3)}GB / {usage.total // (1024**3)}GB)")
        except:
            continue
    return "<br>".join(results)

def get_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return f"{int(f.read()) / 1000:.1f}°C"
    except:
        return "Unavailable"

def get_wifi_status():
    out = run_command("iwconfig")
    return "Connected" if "Link Quality" in out else "Not connected"

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "Unavailable"
    finally:
        s.close()

def get_hostname():
    return platform.node()

def get_sudo_user():
    return os.getenv("SUDO_USER", "Not using sudo")

def get_ssh_config():
    return "Running" if "sshd" in run_command("ps aux") else "Not running"

def get_available_updates():
    return run_command("apt list --upgradable 2>/dev/null").count("\n")

def get_usb_devices():
    return run_command("lsusb") or "None"

# ----- Graph Data Collection -----

def collect_live_data(duration=120, interval=2):
    cpu_data, ram_data, temp_data = [], [], []
    for _ in range(duration // interval):
        cpu_data.append(psutil.cpu_percent())
        ram_data.append(psutil.virtual_memory().percent)
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                temp_data.append(int(f.read()) / 1000)
        except:
            temp_data.append(0)
        time.sleep(interval)
    return cpu_data, ram_data, temp_data

def generate_graph(data, title, ylabel, filename):
    plt.figure()
    plt.plot(data, color="blue")
    plt.title(title)
    plt.xlabel("Time (2s interval)")
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# ----- Report Generator -----

def generate_html(results, cpu_chart, ram_chart, temp_chart):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    filename = f"rpi_diagnostics_{timestamp}.html"
    html = f"""
    <html>
    <head>
        <style>
            body {{ background: white; color: black; text-align: center; font-family: Arial; }}
            table {{ margin: auto; border-collapse: collapse; width: 80%; }}
            th, td {{ border: 1px solid #337ab7; padding: 10px; }}
            th {{ background: #337ab7; color: white; }}
            img {{ margin: 10px auto; display: block; max-width: 90%; }}
        </style>
    </head>
    <body>
        <h2>Raspberry Pi Diagnostic Report</h2>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <table>
            <tr><th>Test</th><th>Result</th></tr>
            {''.join(results)}
        </table>
        <h3>Live Performance Charts (120s)</h3>
        <img src="{cpu_chart}" alt="CPU Usage">
        <img src="{ram_chart}" alt="RAM Usage">
        <img src="{temp_chart}" alt="Temperature">
    </body>
    </html>
    """
    with open(filename, "w") as f:
        f.write(html)
    webbrowser.get(using="chromium").open(f"file://{Path(filename).resolve()}")
    print(f"✅ Report saved to: {filename}")

# ----- Main Runner -----

def run_all_diagnostics():
    print("📊 Running diagnostics and collecting live data for 120s...")
    cpu_data, ram_data, temp_data = collect_live_data()
    print("📈 Generating charts...")

    generate_graph(cpu_data, "CPU Usage Over Time", "% CPU", "cpu_chart.png")
    generate_graph(ram_data, "RAM Usage Over Time", "% RAM", "ram_chart.png")
    generate_graph(temp_data, "CPU Temperature Over Time", "°C", "temp_chart.png")

    results = [
        f"<tr><td>CPU Usage</td><td>{get_cpu_usage()}</td></tr>",
        f"<tr><td>RAM Usage</td><td>{get_ram_usage()}</td></tr>",
        f"<tr><td>Disk Usage</td><td>{get_disk_usage()}</td></tr>",
        f"<tr><td>Temperature</td><td>{get_temp()}</td></tr>",
        f"<tr><td>WiFi Status</td><td>{get_wifi_status()}</td></tr>",
        f"<tr><td>IP Address</td><td>{get_ip_address()}</td></tr>",
        f"<tr><td>Hostname</td><td>{get_hostname()}</td></tr>",
        f"<tr><td>Sudo User</td><td>{get_sudo_user()}</td></tr>",
        f"<tr><td>SSH Config</td><td>{get_ssh_config()}</td></tr>",
        f"<tr><td>Available Updates</td><td>{get_available_updates()}</td></tr>",
        f"<tr><td>USB Devices</td><td><pre>{get_usb_devices()}</pre></td></tr>",
    ]

    print("📝 Generating report...")
    generate_html(results, "cpu_chart.png", "ram_chart.png", "temp_chart.png")

if __name__ == "__main__":
    run_all_diagnostics()
