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

    # Prepare the results
    system_usage_map = {
        "total_ram_gb": round(total_ram, 2),
        "used_ram_gb": round(used_ram, 2),
        "available_ram_gb": round(available_ram, 2),
        "ram_usage_percentage": round(ram_usage_percentage, 2),
        "cpu_usage_percentage": round(cpu_usage_percentage, 2),
        "total_cores": total_cores,
        "total_cpu_threads": total_threads,
        # "cpu_percent_per_core": [round(perc, 2) for perc in cpu_percent_per_core]
    }

    return system_usage_map

# Example usage
if __name__ == "__main__":
    usage = get_system_usage()
    print("System Usage:")
    for key, value in usage.items():
        print(f"{key}: {value}")
