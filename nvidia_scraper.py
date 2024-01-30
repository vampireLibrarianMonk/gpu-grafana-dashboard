import subprocess
import re
import json


def get_nvidia_smi_output():
    metrics = {}

    output = subprocess.check_output(
        [
            'nvidia-smi.json',
            '--query-gpu='
            'name,'
            'driver_version,'
            'vbios_version,' 
            'pstate,'
            'utilization.gpu,'
            'memory.used,'
            'memory.total,'
            'temperature.gpu,'
            'fan.speed,'
            'power.draw,'
            'power.default_limit,'
            'clocks.video,'
            'clocks.sm,'
            'clocks_throttle_reasons.gpu_idle,'
            'clocks_throttle_reasons.hw_thermal_slowdown,'
            'clocks_throttle_reasons.sw_power_cap,'
            'clocks_throttle_reasons.applications_clocks_setting,'
            'clocks_throttle_reasons.hw_power_brake_slowdown,'
            'clocks_throttle_reasons.sw_thermal_slowdown,'
            'clocks_throttle_reasons.sync_boost',
            '--format=csv,noheader,nounits'
        ],
        encoding='utf-8'
    )

    lines = output.strip().split(', ')

    metrics['gpu_name'] = lines[0]
    metrics['driver_version'] = lines[1]
    metrics['vbios_version'] = lines[2]
    metrics['p_state'] = lines[3]
    metrics['gpu_utilization'] = round(float(lines[4]) / 100.0, 2)
    metrics['memory_used'] = int(lines[5])
    metrics['memory_total'] = int(lines[6])
    metrics['memory_utilization'] = round(float(lines[5]) / float(lines[6]), 2)
    metrics['temperature'] = int(lines[7])
    metrics['fan_speed'] = round(float(lines[8]) / 100.0, 2)
    metrics['power.draw'] = float(lines[9])
    metrics['power.default_limit'] = float(lines[10])
    metrics['clocks.video'] = int(lines[11])
    metrics['clocks.sm'] = lines[12]
    metrics['clocks_throttle_reasons.gpu_idle'] = lines[13]
    metrics['clocks_throttle_reasons.hw_thermal_slowdown'] = lines[14]
    metrics['clocks_throttle_reasons.sw_power_cap'] = lines[15]
    metrics['clocks_throttle_reasons.applications_clocks_setting'] = lines[16]
    metrics['clocks_throttle_reasons.hw_power_brake_slowdown'] = lines[17]
    metrics['clocks_throttle_reasons.sw_thermal_slowdown'] = lines[18]
    metrics['clocks_throttle_reasons.sync_boost'] = lines[19]

    special_output = subprocess.check_output(['nvidia-smi.json', '-q', '-d', 'CLOCK'], encoding='utf-8')

    # Regular expressions to find the relevant clock speeds
    current_graphics_clock_regex = r"Graphics\s+:\s+(\d+)\sMHz"
    current_memory_clock_regex = r"Memory\s+:\s+(\d+)\sMHz"
    max_graphics_clock_regex = r"Max Clocks\n\s+Graphics\s+:\s+(\d+)\sMHz"
    max_memory_clock_regex = r"Max Clocks\s*\n\s*Graphics\s*:.*\n\s*SM\s*:.*\n\s*Memory\s*:\s*(\d+)\sMHz"

    # Parse the output
    current_graphics_clock = re.search(current_graphics_clock_regex, special_output)
    current_memory_clock = re.search(current_memory_clock_regex, special_output)
    max_graphics_clock = re.search(max_graphics_clock_regex, special_output)
    max_memory_clock = re.search(max_memory_clock_regex, special_output)

    metrics['current_graphics_clock'] = int(current_graphics_clock.group(1)) if current_graphics_clock else None
    metrics['current_memory_clock'] = int(current_memory_clock.group(1)) if current_memory_clock else None
    metrics['max_graphics_clock'] = int(max_graphics_clock.group(1)) if max_graphics_clock else None
    metrics['max_memory_clock'] = int(max_memory_clock.group(1)) if max_memory_clock else None

    # Extract and return the clock values
    return metrics


def main():
    try:
        metrics = get_nvidia_smi_output()
        print(json.dumps(metrics, indent=4))
    except RuntimeError as err:
        print(err)


if __name__ == '__main__':
    main()
