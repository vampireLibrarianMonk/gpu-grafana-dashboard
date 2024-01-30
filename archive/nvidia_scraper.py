import subprocess
import json
import sys


def parse_nvidia_smi_output(output):
    split_output = output.split(",")
    # official_product_name = split_output[0]
    # p_state = split_output[1]
    gpu_utilization = split_output[2]
    mem_usage = split_output[3]
    mem_total = split_output[4]
    gpu_temperature = split_output[5]
    # fan_speed = split_output[6]
    # power_draw_percentage = split_output[7]

    metrics = {
        # 'official_product_name': official_product_name,
        # 'p_state': p_state,
        'gpu_util_pattern': gpu_utilization,
        'memory_usage_pattern': mem_usage,
        'temperature_pattern': gpu_temperature,
        'mem_total': mem_total
        # 'fan_speed': fan_speed,
        # 'power_draw_percentage': power_draw_percentage
    }

    return metrics


def scrape_nvidia_smi():
    try:
        nvidia_smi_output = subprocess.check_output([
            'nvidia-smi.json',
            '--query-gpu='
            'name,'
            'pstate,'
            'utilization.gpu,'
            'memory.used,'
            'memory.total,'
            'temperature.gpu,'
            'fan.speed,'
            'power.draw',
            '--format=csv,noheader,nounits'],
            encoding='utf-8'
        )
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running nvidia-smi.json: {e}", file=sys.stderr)
        return

    return parse_nvidia_smi_output(nvidia_smi_output)


if __name__ == "__main__":
    metrics = scrape_nvidia_smi()
    if metrics is not None:
        print(json.dumps(metrics, indent=4))
