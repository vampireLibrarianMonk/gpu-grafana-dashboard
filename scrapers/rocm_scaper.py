import json
import re
import subprocess

rocm_smi_commands =         \
    ['rocm-smi',
         '--showdriverversion',
         '--showvbios',
         '--showtemp',
         '--showuse',
         '--showmeminfo', 'vram',
         '--showmemuse',
         '--showvoltage',
         '--showgpuclocks',
         '--showclocks',
         '--showbw',
         '--json']


def parse_rocminfo(input_text):
    agents = {}
    current_agent = {}

    for line in input_text.splitlines():
        name_match = re.match(r'^\s*Name:\s*(.+)', line)
        if name_match:
            # If we're already processing an agent, add it before starting a new one
            if current_agent:
                # Ensure 'Device Type' is present before adding
                if 'Device Type' in current_agent:
                    agents[current_agent['Device Type']] = current_agent
            current_agent = {'Name': name_match.group(1).strip()}  # Reset for new agent

        if current_agent:  # Proceed if we're within an agent block
            marketing_name_match = re.match(r'^\s*Marketing Name:\s*(.+)', line)
            device_type_match = re.match(r'^\s*Device Type:\s*(.+)', line)
            max_clock_freq_match = re.match(r'^\s*Max Clock Freq. \(MHz\):\s*(.+)', line)

            if marketing_name_match:
                current_agent['Marketing Name'] = marketing_name_match.group(1).strip()
            if device_type_match:
                current_agent['Device Type'] = device_type_match.group(1).strip()
            if max_clock_freq_match:
                current_agent['Max Clock Freq. (MHz)'] = max_clock_freq_match.group(1).strip()

    # Add the last agent if it hasn't been added yet
    if current_agent and 'Device Type' in current_agent:
        agents[current_agent['Name']] = current_agent

    return agents


def parse_rocmsmi(json_data):
    holder = {}
    parsed_data = {}

    for device, attributes in json_data.items():
        if device == "card0":
            parsed_data["VBIOS version"] = attributes.get("VBIOS version")
            parsed_data["Temperature (Sensor edge)"] = attributes.get("Temperature (Sensor edge) (C)")
            parsed_data["Temperature (Sensor junction)"] = attributes.get("Temperature (Sensor junction) (C)")
            parsed_data["Temperature (Sensor memory)"] = attributes.get("Temperature (Sensor memory) (C)")
            parsed_data["VRAM Total Memory (B)"] = attributes.get("VRAM Total Memory (B)")
            parsed_data["VRAM Total Used Memory (B)"] = attributes.get("VRAM Total Used Memory (B)")
            parsed_data["GPU memory use (%)"] = attributes.get("GPU memory use (%)")
            parsed_data["GPU use (%)"] = attributes.get("GPU use (%)")
            parsed_data["Memory Activity"] = attributes.get("Memory Activity")
            parsed_data["Avg. Memory Bandwidth"] = attributes.get("Avg. Memory Bandwidth")
            parsed_data["Voltage (mV)"] = attributes.get("Voltage (mV)")
            parsed_data["Display Clock Level"] = attributes.get("dcefclk clock speed:").replace("(", "").replace(")",
                                                                                                                 "")
            parsed_data["Display Clock Speed"] = attributes.get("dcefclk clock level:")
            parsed_data["Fabric Clock Speed"] = attributes.get("fclk clock speed:").replace("(", "").replace(")", "")
            parsed_data["Fabric Clock Level"] = attributes.get("fclk clock level:")
            parsed_data["Memory Clock Speed"] = attributes.get("mclk clock speed:").replace("(", "").replace(")", "")
            parsed_data["Memory Clock Level"] = attributes.get("mclk clock level:")
            parsed_data["Shader Clock Speed"] = attributes.get("sclk clock speed:").replace("(", "").replace(")", "")
            parsed_data["Shader Clock Level"] = attributes.get("sclk clock level:")
            parsed_data["System on Chip Clock Speed"] = attributes.get("socclk clock speed:").replace("(", "").replace(
                ")", "")
            parsed_data["System on Chip Clock Level"] = attributes.get("socclk clock level:")
            parsed_data["Peripheral Component Interconnect Express (PCIe)"] = attributes.get("pcie clock level")
            parsed_data["Estimated maximum PCIe bandwidth over the last second (MB/s)"] = attributes.get(
                "Estimated maximum PCIe bandwidth over the last second (MB/s)")
        elif device == "system":
            parsed_data["Driver version"] = attributes.get("Driver version")

    holder["GPU_Details"] = parsed_data

    return holder


def get_rocm_smi_output():
    metrics = {}

    rocm_smi_output = subprocess.run(
        rocm_smi_commands,
        capture_output=True,
        text=True
    )

    rocm_info_output = subprocess.run(
        ['rocminfo'],
        capture_output=True,
        text=True
    )

    if rocm_info_output.returncode == 0:
        rocm_info_agent = parse_rocminfo(rocm_info_output.stdout)
    else:
        raise RuntimeError("Error executing rocminfo:", rocm_info_output.stderr)

    metrics['gpu_name'] = f'{rocm_info_agent["GPU"]["Marketing Name"]} ({rocm_info_agent["GPU"]["Name"]})'

    if rocm_smi_output.returncode == 0:
        rocm_smi_agent = parse_rocmsmi(json.loads(rocm_smi_output.stdout))
    else:
        raise RuntimeError("Error executi ng rocm-smi:", rocm_smi_output.stderr)

    metrics['driver_version'] = rocm_smi_agent["GPU_Details"]["Driver version"]
    metrics['vbios_version'] = rocm_smi_agent["GPU_Details"]["VBIOS version"]
    # metrics['p_state'] = lines[3]
    metrics['gpu_utilization'] = round(float(rocm_smi_agent["GPU_Details"]["GPU use (%)"]) / 100.0, 2)
    metrics['memory_used'] = int(rocm_smi_agent["GPU_Details"]["VRAM Total Used Memory (B)"])
    metrics['memory_total'] = int(rocm_smi_agent["GPU_Details"]["VRAM Total Memory (B)"])
    metrics['memory_utilization'] = round(float(metrics['memory_used']) / float(metrics['memory_total']), 2)
    metrics['temperature_sensor_edge'] = float(rocm_smi_agent["GPU_Details"]["Temperature (Sensor edge)"])
    metrics['temperature_sensor_junction'] = float(rocm_smi_agent["GPU_Details"]["Temperature (Sensor junction)"])
    metrics['temperature_sensor_memory'] = float(rocm_smi_agent["GPU_Details"]["Temperature (Sensor memory)"])
    # metrics['fan_speed'] = round(float(lines[8]) / 100.0, 2)
    # metrics['power.draw'] = float(lines[9])
    # metrics['power.default_limit'] = float(lines[10])
    # metrics['clocks.video'] = int(lines[11])
    # metrics['clocks.sm'] = lines[12]
    # metrics['clocks_throttle_reasons.gpu_idle'] = lines[13]
    # metrics['clocks_throttle_reasons.hw_thermal_slowdown'] = lines[14]
    # metrics['clocks_throttle_reasons.sw_power_cap'] = lines[15]
    # metrics['clocks_throttle_reasons.applications_clocks_setting'] = lines[16]
    # metrics['clocks_throttle_reasons.hw_power_brake_slowdown'] = lines[17]
    # metrics['clocks_throttle_reasons.sw_thermal_slowdown'] = lines[18]
    # metrics['clocks_throttle_reasons.sync_boost'] = lines[19]

    special_output = subprocess.check_output(['nvidia-smi', '-q', '-d', 'CLOCK'], encoding='utf-8')

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
    rocm_info_output = subprocess.run(
        ['rocminfo'],
        capture_output=True,
        text=True
    )

    if rocm_info_output.returncode == 0:
        agents = parse_rocminfo(rocm_info_output.stdout)
        print(json.dumps(agents, indent=4))
    else:
        print("Error executing rocminfo:", rocm_info_output.stderr)

    rocm_smi_output = subprocess.run(
        rocm_smi_commands,
        capture_output=True,
        text=True
    )

    if rocm_smi_output.returncode == 0:
        parsed_json = parse_rocmsmi(json.loads(rocm_smi_output.stdout))
        print(json.dumps(parsed_json, indent=4))
    else:
        print("Error executing rocm-smi:", rocm_smi_output.stderr)


if __name__ == "__main__":
    main()
