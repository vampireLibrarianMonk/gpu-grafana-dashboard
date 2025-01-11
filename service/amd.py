import time
import schedule
import threading
from prometheus_client import Gauge, start_http_server
from scrapers.rocm_scaper import get_rocm_smi_output

# Define Prometheus metrics
gpu_name = Gauge('rocm_smi_gpu_name', 'GPU Name', ['gpu_name'])
driver_version = Gauge('rocm_smi_driver_version', 'Driver Version', ['driver_version'])
vbios_version = Gauge('rocm_smi_vbios_version', 'VBIOS Version', ['vbios_version'])
p_state = Gauge('rocm_smi_p_state', 'Performance Level', ['p_state'])
gpu_utilization = Gauge('rocm_smi_utilization_gpu_ratio', 'GPU Utilization Ratio')
memory_utilization = Gauge('rocm_smi_utilization_memory_ratio', 'Memory Utilization Ratio')
memory_used = Gauge('rocm_smi_memory_used_bytes', 'Memory Used in Bytes')
memory_total = Gauge('rocm_smi_memory_total_bytes', 'Total Memory in Bytes')
temperature = Gauge('rocm_smi_temperature_gpu', 'GPU Temperature')
fan_speed = Gauge('rocm_smi_fan_speed', 'Fan Speed')
current_graphics_clock = Gauge('rocm_smi_clocks_current_graphics_clock_hz', 'Current Graphics Clock in Hz')
current_memory_clock = Gauge('rocm_smi_clocks_current_memory_clock_hz', 'Current Memory Clock in Hz')
power_draw = Gauge('rocm_smi_power_draw_watts', 'Power Draw in Watts')
power_default_limit = Gauge('rocm_smi_power_default_limit_watts', 'Power Default Limit in Watts')


def fetch_metrics():
    metrics = get_rocm_smi_output()

    # Set metrics with labels
    gpu_name.labels(gpu_name=metrics['gpu_name']).set(1)
    driver_version.labels(driver_version=metrics['driver_version']).set(1)
    vbios_version.labels(vbios_version=metrics['vbios_version']).set(1)
    p_state.labels(p_state=metrics['p_state']).set(1)

    # Set metrics without labels
    gpu_utilization.set(metrics["gpu_utilization"])
    memory_utilization.set(metrics["memory_utilization"])
    memory_used.set(metrics["memory_used"])
    memory_total.set(metrics["memory_total"])
    temperature.set(metrics["temperature"])
    fan_speed.set(metrics["fan_speed"])
    current_graphics_clock.set(metrics["current_graphics_clock"])
    current_memory_clock.set(metrics["current_memory_clock"])
    power_draw.set(metrics["power.draw"])
    power_default_limit.set(metrics["power.default_limit"])


def run_scheduler():
    schedule.every(1).seconds.do(fetch_metrics)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    # Start the Prometheus metrics server on port 8000
    start_http_server(8000)
    print('Metrics server running on port 8000')

    # Start the metrics fetching scheduler
    fetch_metrics()  # Initial fetch to populate metrics
    threading.Thread(target=run_scheduler, daemon=True).start()

    # Keep the main thread alive
    while True:
        time.sleep(10)
