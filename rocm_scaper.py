import json
import re
import subprocess


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
            parsed_data["GPU memory use (%)"] = attributes.get("GPU memory use (%)")
            parsed_data["Memory Activity"] = attributes.get("Memory Activity")
            parsed_data["Avg. Memory Bandwidth"] = attributes.get("Avg. Memory Bandwidth")
            parsed_data["Voltage (mV)"] = attributes.get("Voltage (mV)")
            parsed_data["Display Clock Level"] = attributes.get("dcefclk clock speed:").replace("(","").replace(")","")
            parsed_data["Display Clock Speed"] = attributes.get("dcefclk clock level:")
            parsed_data["Fabric Clock Speed"] = attributes.get("fclk clock speed:").replace("(","").replace(")","")
            parsed_data["Fabric Clock Level"] = attributes.get("fclk clock level:")
            parsed_data["Memory Clock Speed"] = attributes.get("mclk clock speed:").replace("(","").replace(")","")
            parsed_data["Memory Clock Level"] = attributes.get("mclk clock level:")
            parsed_data["Shader Clock Speed"] = attributes.get("sclk clock speed:").replace("(","").replace(")","")
            parsed_data["Shader Clock Level"] = attributes.get("sclk clock level:")
            parsed_data["System on Chip Clock Speed"] = attributes.get("socclk clock speed:").replace("(","").replace(")","")
            parsed_data["System on Chip Clock Level"] = attributes.get("socclk clock level:")
            parsed_data["Peripheral Component Interconnect Express (PCIe)"] = attributes.get("pcie clock level")
            parsed_data["Estimated maximum PCIe bandwidth over the last second (MB/s)"] = attributes.get("Estimated maximum PCIe bandwidth over the last second (MB/s)")
        elif device == "system":
            parsed_data["Driver version"] = attributes.get("Driver version")

    holder["GPU_Details"] = parsed_data

    return holder


def main():
    resultOne = subprocess.run(
        ['rocminfo'],
        capture_output=True,
        text=True
    )

    if resultOne.returncode == 0:
        agents = parse_rocminfo(resultOne.stdout)
        print(json.dumps(agents, indent=4))
    else:
        print("Error executing rocminfo:", resultOne.stderr)

    resultTwo = subprocess.run(
        ['rocm-smi',
         '--showdriverversion',
         '--showvbios',
         '--showtemp',
         '--showmemuse',
         '--showvoltage',
         '--showgpuclocks',
         '--showclocks',
         '--showbw',
         '--json'],
        capture_output=True,
        text=True
    )

    if resultTwo.returncode == 0:
        parsed_json = parse_rocmsmi(json.loads(resultTwo.stdout))
        print(json.dumps(parsed_json, indent=4))
    else:
        print("Error executing rocm-smi:", resultTwo.stderr)


if __name__ == "__main__":
    main()
