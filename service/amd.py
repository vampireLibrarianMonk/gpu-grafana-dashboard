import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import schedule
import threading
from scrapers.rocm_scaper import get_rocm_smi_output

latest_metrics = []


def format_prometheus_metrics(metrics):
    prometheus_metrics = ''

    gpu_name = metrics["gpu_name"]
    driver_version = metrics["driver_version"]
    # vbios_version = metrics["vbios_version"]
    # prometheus_metrics += f'nvidia_smi_gpu_name{{gpu_name="{gpu_name}"}} 1\n'
    # prometheus_metrics += f'nvidia_smi_gpu_driver{{driver_version="{driver_version}"}} 1\n'
    # prometheus_metrics += f'nvidia_smi_gpu_vbios{{vbios_version="{vbios_version}"}} 1\n'
    # prometheus_metrics += f'nvidia_smi_pstate{{p_state_info="{metrics["p_state"]}"}} 1\n'
    # prometheus_metrics += f'nvidia_smi_utilization_gpu_ratio{{}} {metrics["gpu_utilization"]}\n'
    # prometheus_metrics += f'nvidia_smi_utilization_memory_ratio{{}} {metrics["memory_utilization"]}\n'
    # prometheus_metrics += f'nvidia_smi_memory_used_bytes{{}} {metrics["memory_used"]}\n'
    # prometheus_metrics += f'nvidia_smi_memory_total_bytes{{}} {metrics["memory_total"]}\n'
    # prometheus_metrics += f'nvidia_memory_total{{}} {metrics["memory_total"]}\n'
    # prometheus_metrics += f'nvidia_smi_temperature_gpu{{}} {metrics["temperature"]}\n'
    # prometheus_metrics += f'nvidia_fan_speed{{}} {metrics["fan_speed"]}\n'
    # prometheus_metrics += f'nvidia_smi_clocks_current_graphics_clock_hz{{}} {metrics["current_graphics_clock"]}\n'
    # prometheus_metrics += f'nvidia_smi_clocks_max_graphics_clock_hz{{}} {metrics["max_graphics_clock"]}\n'
    # prometheus_metrics += f'nvidia_smi_clocks_current_memory_clock_hz{{}} {metrics["current_memory_clock"]}\n'
    # prometheus_metrics += f'nvidia_smi_clocks_max_memory_clock_hz{{}} {metrics["max_memory_clock"]}\n'
    # prometheus_metrics += f'nvidia_smi_fan_speed_ratio{{}} {metrics["fan_speed"]}\n'
    # prometheus_metrics += f'nvidia_smi_power_draw_watts{{}} {metrics["power.draw"]}\n'
    # prometheus_metrics += f'nvidia_smi_power_default_limit_watts{{}} {metrics["power.default_limit"]}\n'
    # prometheus_metrics += f'nvidia_smi_clocks_current_video_clock_hz{{}} {metrics["clocks.video"]}\n'
    # prometheus_metrics += f'nvidia_smi_clocks_current_sm_clock_hz{{}} {metrics["clocks.sm"]}\n'
    #
    # prometheus_metrics += f'nvidia_smi_clocks_throttle_reasons_gpu_idle{{gpu_idle="{metrics["clocks_throttle_reasons.gpu_idle"]}"}} {1 if metrics["clocks_throttle_reasons.gpu_idle"] == "Active" else 0}\n'
    # prometheus_metrics += f'nvidia_smi_clocks_throttle_reasons_hw_thermal_slowdown{{hw_thermal_slowdown="{metrics["clocks_throttle_reasons.hw_thermal_slowdown"]}"}} {1 if metrics["clocks_throttle_reasons.hw_thermal_slowdown"] == "Active" else 0}\n'
    # prometheus_metrics += f'nvidia_smi_clocks_throttle_reasons_sw_power_cap{{sw_power_cap="{metrics["clocks_throttle_reasons.sw_power_cap"]}"}} {1 if metrics["clocks_throttle_reasons.sw_power_cap"] == "Active" else 0}\n'
    # prometheus_metrics += f'nvidia_smi_clocks_throttle_reasons_applications_clocks_setting{{clocks_setting="{metrics["clocks_throttle_reasons.applications_clocks_setting"]}"}} {1 if metrics["clocks_throttle_reasons.applications_clocks_setting"] == "Active" else 0}\n'
    # prometheus_metrics += f'nvidia_smi_clocks_throttle_reasons_hw_power_brake_slowdown{{brake_slowdown="{metrics["clocks_throttle_reasons.hw_power_brake_slowdown"]}"}} {1 if metrics["clocks_throttle_reasons.hw_power_brake_slowdown"] == "Active" else 0}\n'
    # prometheus_metrics += f'nvidia_smi_clocks_throttle_reasons_sw_thermal_slowdown{{sw_thermal_slowdown="{metrics["clocks_throttle_reasons.sw_thermal_slowdown"]}"}} {1 if metrics["clocks_throttle_reasons.sw_thermal_slowdown"] == "Active" else 0}\n'
    # prometheus_metrics += f'nvidia_smi_clocks_throttle_reasons_sync_boost{{sync_boost="{metrics["clocks_throttle_reasons.sync_boost"]}"}} {1 if metrics["clocks_throttle_reasons.sync_boost"] == "Active" else 0}\n'

    return prometheus_metrics


def fetch_metrics():
    global latest_metrics
    latest_metrics = get_rocm_smi_output()


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            formatted_metrics = format_prometheus_metrics(latest_metrics)
            self.wfile.write(formatted_metrics.encode())
        else:
            self.send_response(404)
            self.end_headers()


def run_server():
    port = 8000
    server_address = ('', port)
    try:
        httpd = HTTPServer(server_address, MetricsHandler)
        print(f'Starting metrics server on port {port}')
        httpd.serve_forever()
    except Exception as e:
        print(f"Failed to start server: {e}")


def run_scheduler():
    schedule.every(1).seconds.do(fetch_metrics)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    fetch_metrics()
    thread = threading.Thread(target=run_scheduler)
    thread.start()
    run_server()
