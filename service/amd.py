import time
import schedule
import threading
from prometheus_client import Gauge, start_http_server
from utilities.utilities_rocm_gpu import get_gpu_info
from utilities.utilities_cpu_ram import get_system_usage

# Define Prometheus metrics
## GPU
gpu_name = Gauge('rocm_smi_gpu_name', 'GPU Name', ['gpu_name'])
driver_version = Gauge('rocm_smi_driver_version', 'Driver Version', ['driver_version'])
vbios_version = Gauge('rocm_smi_vbios_version', 'VBIOS Version', ['vbios_version'])
p_state = Gauge('rocm_smi_p_state', 'Performance Level', ['p_state'])
gpu_utilization = Gauge('rocm_smi_utilization_gpu_ratio', 'GPU Utilization Ratio')
gpu_memory_utilization = Gauge('rocm_smi_utilization_memory_ratio', 'Memory Utilization Ratio')
gpu_memory_used = Gauge('rocm_smi_memory_used_bytes', 'Memory Used in Bytes')
gpu_memory_total = Gauge('rocm_smi_memory_total_bytes', 'Total Memory in Bytes')
gpu_temperature = Gauge('rocm_smi_temperature_gpu', 'GPU Temperature')
gpu_fan_speed = Gauge('rocm_smi_fan_speed', 'Fan Speed')
current_graphics_clock = Gauge('rocm_smi_clocks_current_graphics_clock_hz', 'Current Graphics Clock in Hz')
gpu_current_memory_clock = Gauge('rocm_smi_clocks_current_memory_clock_hz', 'Current Memory Clock in Hz')
power_draw = Gauge('rocm_smi_power_draw_watts', 'Power Draw in Watts')
power_default_limit = Gauge('rocm_smi_power_default_limit_watts', 'Power Default Limit in Watts')

## CPU
usage_cpu_percentage = Gauge('cpu_usage_percentage', 'CPU usage percentage')
total_cpu_cores = Gauge('total_cores', 'Total CPU cores')
total_cpu_threads = Gauge('total_cpu_threads', 'Total CPU threads')
tccd1_temp_cpu = Gauge('tccd_temp_cpu_one', 'Core Complex Die Temperature 1')
tccd2_temp_cpu = Gauge('tccd_temp_cpu_two', 'Core Complex Die Temperature 2')

## RAM
total_ram_gb = Gauge('total_ram_gb', 'Total RAM Available in Gigabytes')
used_ram_gb = Gauge('used_ram_gb', 'Used RAM in Gigabytes')
available_ram_gb = Gauge('available_ram_gb', 'Available Ram in Gigabytes')
ram_usage_percentage = Gauge('ram_usage_percentage', 'RAM usage percentage')


def fetch_metrics():
    gpu_metrics = get_gpu_info()
    cpu_ram_metrics = get_system_usage()

    # Set metrics with labels
    gpu_name.labels(gpu_name=gpu_metrics['gpu_name']).set(1)
    driver_version.labels(driver_version=gpu_metrics['driver_version']).set(1)
    vbios_version.labels(vbios_version=gpu_metrics['vbios_version']).set(1)
    p_state.labels(p_state=gpu_metrics['p_state']).set(1)

    # Set metrics without labels
    ## GPU
    gpu_utilization.set(gpu_metrics["gpu_utilization"])
    gpu_memory_utilization.set(gpu_metrics["memory_utilization"])
    gpu_memory_used.set(gpu_metrics["memory_used"])
    gpu_memory_total.set(gpu_metrics["memory_total"])
    gpu_temperature.set(gpu_metrics["temperature"])
    gpu_fan_speed.set(gpu_metrics["fan_speed"])
    current_graphics_clock.set(gpu_metrics["current_graphics_clock"])
    gpu_current_memory_clock.set(gpu_metrics["current_memory_clock"])
    power_draw.set(gpu_metrics["power.draw"])
    power_default_limit.set(gpu_metrics["power.default_limit"])

    ## CPU
    usage_cpu_percentage.set(cpu_ram_metrics['cpu_usage_percentage'])
    total_cpu_cores.set(cpu_ram_metrics['total_cores'])
    total_cpu_threads.set(cpu_ram_metrics['total_cpu_threads'])
    tccd1_temp_cpu.set(cpu_ram_metrics['cpu_tccd1_temp'])
    tccd2_temp_cpu.set(cpu_ram_metrics['cpu_tccd2_temp'])

    ## RAM
    total_ram_gb.set(cpu_ram_metrics['total_ram_gb'])
    used_ram_gb.set(cpu_ram_metrics['used_ram_gb'])
    available_ram_gb.set(cpu_ram_metrics['available_ram_gb'])
    ram_usage_percentage.set(cpu_ram_metrics['ram_usage_percentage'])


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
