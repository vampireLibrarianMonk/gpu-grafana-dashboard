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
                    agents[current_agent['Name']] = current_agent
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


def main():
    result = subprocess.run(['rocminfo'], capture_output=True, text=True)

    if result.returncode == 0:
        agents = parse_rocminfo(result.stdout)
        print(json.dumps(agents, indent=4))
    else:
        print("Error executing rocminfo:", result.stderr)


if __name__ == "__main__":
    main()
