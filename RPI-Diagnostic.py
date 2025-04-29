#!/usr/bin/env python3

import os
import time
import socket
import subprocess
import psutil
import datetime
import matplotlib.pyplot as plt
import webbrowser
from tkinter import Tk, filedialog

# For tracking results
test_results = []
stress_test_graph = None

def print_banner():
    banner = r"""
██████╗ ██████╗ ██╗   ██╗██████╗ ██████╗ ██╗ ██████╗  █████╗  ██████╗██╗  ██╗
██╔══██╗██╔══██╗██║   ██║██╔══██╗██╔══██╗██║██╔════╝ ██╔══██╗██╔════╝██║ ██╔╝
██████╔╝██████╔╝██║   ██║██║  ██║██████╔╝██║██║  ███╗███████║██║     █████╔╝ 
██╔═══╝ ██╔═══╝ ██║   ██║██║  ██║██╔═══╝ ██║██║   ██║██╔══██║██║     ██╔═██╗ 
██║     ██║     ╚██████╔╝██████╔╝██║     ██║╚██████╔╝██║  ██║╚██████╗██║  ██╗
╚═╝     ╚═╝      ╚═════╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
                  Raspberry Pi Diagnostic Tool 🚀
    """
    print(banner)
    print("=" * 80)

def check_cpu_temp():
    try:
        output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        temp = float(output.replace("temp=", "").replace("'C\n", ""))
        return temp
    except Exception:
        return None

def check_gpu_temp():
    try:
        output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        temp = float(output.replace("temp=", "").replace("'C\n", ""))
        return temp
    except Exception:
        return None

def check_ram():
    try:
        ram = psutil.virtual_memory()
        return ram.percent
    except Exception:
        return None

def check_wifi_signal():
    try:
        output = subprocess.check_output(["iwconfig"], stderr=subprocess.DEVNULL).decode()
        for line in output.split("\n"):
            if "Link Quality" in line:
                quality = line.strip().split(" ")[1].split("=")[1]
                return quality
        return None
    except Exception:
        return None

def check_disk_usage():
    try:
        usage = psutil.disk_usage('/')
        return usage.percent
    except Exception:
        return None

def check_internet_speed():
    try:
        import speedtest
        st = speedtest.Speedtest()
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        return download_speed
    except Exception:
        return None

def check_throttling():
    try:
        output = subprocess.check_output(["vcgencmd", "get_throttled"]).decode()
        return output.strip()
    except Exception:
        return None

def cpu_stress_test(duration=120):
    global stress_test_graph
    import threading

    cpu_temps = []
    timestamps = []

    def stress():
        while not stop_event.is_set():
            [x**2 for x in range(10000)]

    stop_event = threading.Event()
    stress_thread = threading.Thread(target=stress)
    stress_thread.start()

    print(f"🚀 Running CPU stress test for {duration} seconds...")
    start_time = time.time()
    while time.time() - start_time < duration:
        temp = check_cpu_temp()
        if temp:
            cpu_temps.append(temp)
            timestamps.append(time.time() - start_time)
        time.sleep(1)
        # Animated progress bar
        progress = int((time.time() - start_time) / duration * 30)
        print(f"\rProgress: [{'#' * progress}{'.' * (30 - progress)}] {int((time.time() - start_time)/duration*100)}%", end="")

    stop_event.set()
    stress_thread.join()
    print("\n✅ Stress test complete!")

    # Generate graph
    plt.figure(figsize=(10,5))
    plt.plot(timestamps, cpu_temps, marker='o')
    plt.title("CPU Temp During Stress Test")
    plt.xlabel("Time (s)")
    plt.ylabel("CPU Temp (°C)")
    plt.grid(True)
    stress_test_graph = "stress_test_graph.png"
    plt.savefig(stress_test_graph)
    plt.close()

def generate_html_report(path):
    html_rows = []
    for test, (status, result) in test_results:
        icon = "✅" if status else "❌"
        html_rows.append(f"<tr><td>{test}</td><td>{icon} {result}</td></tr>")

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial; background-color: #ffffff; color: #000; text-align: center; }}
            table {{ margin: 0 auto; border-collapse: collapse; width: 80%; margin-top: 20px; }}
            th, td {{ padding: 10px; text-align: center; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #4CAF50; color: white; }}
            img {{ margin-top: 20px; max-width: 90%; height: auto; }}
        </style>
    </head>
    <body>
        <h2>🖥️ Raspberry Pi Diagnostic Report</h2>
        <p>Generated: {datetime.datetime.now()}</p>
        <table>
            <tr><th>Test</th><th>Result</th></tr>
            {''.join(html_rows)}
        </table>
    """

    if stress_test_graph and os.path.exists(stress_test_graph):
        html += f"<h3>CPU Temperature During Stress Test</h3><img src='{stress_test_graph}' alt='Stress Test Graph'>"

    html += """
    </body>
    </html>
    """

    with open(path, "w") as f:
        f.write(html)

def save_html_with_popup():
    Tk().withdraw()
    path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML files", "*.html")])
    if path:
        generate_html_report(path)
        print(f"✅ Report saved to {path}")
        webbrowser.open(f"file://{os.path.abspath(path)}")
    else:
        print("❌ Report save cancelled.")

def main():
    print_banner()

    # CPU Temp
    cpu_temp = check_cpu_temp()
    test_results.append(("CPU Temp", (cpu_temp is not None, f"{cpu_temp:.2f} °C" if cpu_temp else "N/A")))

    # GPU Temp
    gpu_temp = check_gpu_temp()
    test_results.append(("GPU Temp", (gpu_temp is not None, f"{gpu_temp:.2f} °C" if gpu_temp else "N/A")))

    # RAM Usage
    ram_usage = check_ram()
    test_results.append(("RAM Usage", (ram_usage is not None, f"{ram_usage:.2f} %" if ram_usage else "N/A")))

    # WiFi Signal
    wifi_quality = check_wifi_signal()
    test_results.append(("WiFi Signal Quality", (wifi_quality is not None, wifi_quality if wifi_quality else "N/A")))

    # Disk Usage
    disk_usage = check_disk_usage()
    test_results.append(("Disk Usage", (disk_usage is not None, f"{disk_usage:.2f} %" if disk_usage else "N/A")))

    # Internet Speed
    download_speed = check_internet_speed()
    test_results.append(("Internet Download Speed", (download_speed is not None, f"{download_speed:.2f} Mbps" if download_speed else "N/A")))

    # Throttling
    throttled = check_throttling()
    test_results.append(("CPU Throttling", ("0x0" in throttled if throttled else False, throttled)))

    # Run Stress Test
    cpu_stress_test()

    # Save HTML
    save_html_with_popup()

if __name__ == "__main__":
    main()
