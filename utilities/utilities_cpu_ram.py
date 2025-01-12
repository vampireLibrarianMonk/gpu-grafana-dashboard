import psutil

def get_system_usage():
    """
    Outputs the current RAM and CPU usage, along with total available RAM and total CPU threads.

    Returns:
        dict: A dictionary containing RAM and CPU usage information.
    """
    # Get memory info
    memory_info = psutil.virtual_memory()
    total_ram = memory_info.total / (1024 ** 3)  # Convert bytes to GB
    used_ram = memory_info.used / (1024 ** 3)   # Convert bytes to GB
    available_ram = memory_info.available / (1024 ** 3)  # Convert bytes to GB
    ram_usage_percentage = memory_info.percent

    # Get CPU info
    cpu_usage_percentage = psutil.cpu_percent(interval=1) / 100.0  # 1-second interval for more accurate usage
    total_cores = psutil.cpu_count(logical=False)  # Physical cores
    total_threads = psutil.cpu_count(logical=True)  # Logical threads
    # cpu_percent_per_core = psutil.cpu_percent(interval=1, percpu=True)  # CPU usage per core

    # Get CPU temps Core Complex Die (CCD) Temperature
    cpu_ccd_temps = get_cpu_temperatures()

    # Prepare the results
    system_usage_map = {
        "total_ram_gb": round(total_ram, 2),
        "used_ram_gb": round(used_ram, 2),
        "available_ram_gb": round(available_ram, 2),
        "ram_usage_percentage": round(ram_usage_percentage, 2),
        "cpu_usage_percentage": round(cpu_usage_percentage, 2),
        "total_cores": total_cores,
        "total_cpu_threads": total_threads,
        "cpu_tccd1_temp": int(cpu_ccd_temps['Tccd1']),
        "cpu_tccd2_temp": int(cpu_ccd_temps['Tccd2'])
        # "cpu_percent_per_core": [round(perc, 2) for perc in cpu_percent_per_core]
    }

    return system_usage_map


def get_cpu_temperatures():
    """
    Retrieves CPU temperature readings from the k10temp sensor.

    Returns:
        dict: A dictionary containing temperature readings, or an error message if unavailable.
    """
    try:
        # Fetch all temperature sensors
        temps = psutil.sensors_temperatures()

        # Check if 'k10temp' sensor data is available
        if 'k10temp' in temps:
            k10temp_readings = temps['k10temp']
            temperature_data = {}

            # Extract temperature readings
            for entry in k10temp_readings:
                if 'tccd1' in entry.label.lower():
                    label = entry.label if entry.label else 'Error (Tccd1).'
                    temperature_data[label] = round(entry.current)
                if 'tccd2' in entry.label.lower():
                    label = entry.label if entry.label else 'Error (Tccd2).'
                    temperature_data[label] = round(entry.current)

            return temperature_data
        else:
            return {"error": "k10temp sensor not found. Ensure it's available on your system."}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}

# Example usage
if __name__ == "__main__":
    usage = get_system_usage()
    print("System Usage:")
    for key, value in usage.items():
        print(f"{key}: {value}")
    #
    # from cpuinfo import get_cpu_info
    #
    #
    # def get_detailed_cpu_info():
    #     cpu_info = get_cpu_info()
    #     return cpu_info
    #
    #
    # if __name__ == "__main__":
    #     detailed_info = get_detailed_cpu_info()
    #     print("\nDetailed CPU Information:")
    #     for key, value in detailed_info.items():
    #         print(f"{key}: {value}")

