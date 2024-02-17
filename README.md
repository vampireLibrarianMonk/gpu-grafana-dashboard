# GPU Dashboard
Prometheus and Grafana are cornerstone tools in modern infrastructure for monitoring and visualization, offering deep 
insights into system performance and health. Prometheus specializes in data collection and alerting, providing a robust 
query language, while Grafana excels in data visualization, allowing for the creation of detailed dashboards from 
multiple data sources. Together, they form a powerful toolkit for real-time monitoring and analysis, essential for 
maintaining system reliability and performance.

## Prometheus:
Open-source monitoring system designed for reliability and efficiency.

Features:
      * Dimensional data model: Supports time series data identified by metric name and key/value pairs.
      * PromQL: A powerful query language for data analysis and aggregation.
      * Autonomous single server nodes: No dependence on distributed storage.
      * Service discovery: Automates the discovery of monitoring targets.
      * Pull-based collection: Simplifies configuration and ensures up-to-date data.

## Grafana:
Open-source visualization and analytics software, perfect for creating interactive dashboards.

Features:
      * Rich visualization options: Supports various graph, table, and panel formats.
      * Dynamic Dashboards: Enhances user interaction with template variables.
      * Mixed Data Sources: Integrates data from Prometheus and other sources seamlessly.
      * Extensible: Supports plugins for additional data sources and visualizations.
      * Advanced alerting: Offers comprehensive alerting and notification systems.

## Synergy:

  * Comprehensive Monitoring: Offering a complete monitoring solution, from data collection to detailed visualization.
  * Real-Time Insights: Enable real-time performance and health monitoring of systems and applications.
  * Problem Diagnosis and Alerting: Facilitate quick identification of issues and alerting for immediate action.
  * Customizable and Scalable: Meet the needs of small projects to large-scale enterprise environments.

By leveraging Prometheus for its robust monitoring and alerting capabilities alongside Grafana for its advanced 
visualization features, teams can achieve a deep understanding of their systems' operational state, ensuring optimal 
performance and reliability.

## NVIDIA-SMI and ROCm-SMI Integration with Prometheus and Grafana

NVIDIA-SMI (NVIDIA System Management Interface) and ROCm-SMI (Radeon Open Compute System Management Interface) are 
command-line utilities designed for monitoring and managing hardware functionalities of NVIDIA and AMD GPUs, 
respectively. These tools provide critical insights into the performance, temperature, power usage, and other key 
metrics of GPUs, making them indispensable for system administrators, developers, and data scientists working in 
GPU-intensive environments. Integrating NVIDIA-SMI and ROCm-SMI with Prometheus and Grafana offers a unified interface 
for real-time hardware monitoring, enhancing system performance and reliability.

## Implementation:

To achieve this integration, users need to set up Prometheus to scrape GPU metrics exposed by custom exporters for 
NVIDIA-SMI and ROCm-SMI. Grafana can then connect to Prometheus as a data source, allowing users to create dashboards 
that visualize these metrics in real-time. This setup empowers users to monitor their GPU hardware efficiently, ensuring
optimal performance and longevity of their devices.

1. Add Grafana's GPG key and repository
```bash
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
```

2. Add the Grafana repository to your system's software sources
```bash
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
```

3. Update your package lists
```bash
sudo apt-get update
```

4. Install Grafana
```bash
sudo apt-get install grafana
```

5. Start grafana server
```bash
sudo systemctl start grafana-server
```

6. Enable Grafana to start at boot
```bash
sudo systemctl enable grafana-server
```

7. Install Prometheus
```bash
sudo apt-get install prometheus -y
```

8. Start the Prometheus service
```bash
sudo systemctl start prometheus
```

9. Enable Prometheus to start at boot
```bash
sudo systemctl enable prometheus
```

10. Update Prometheus Configuration (amd or nvidia)
```bash
sudo prometheus/{GPU_CHIPSET_MANUFACTURER}.yml /etc/prometheus/{GPU_CHIPSET_MANUFACTURER}.yml
```

11. Reload Prometheus to apply the configuration changes
```bash
sudo systemctl reload prometheus
```

12. Check the status of Prometheus to ensure it is running as expected
```bash
sudo systemctl status prometheus
```

Result:
```bash
● prometheus.service - Monitoring system and time series database
     Loaded: loaded (/lib/systemd/system/prometheus.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2024-02-16 20:24:16 EST; 3min 32s ago
       Docs: https://prometheus.io/docs/introduction/overview/
             man:prometheus(1)
    Process: 8401 ExecReload=/bin/kill -HUP $MAINPID (code=exited, status=0/SUCCESS)
   Main PID: 8056 (prometheus)
      Tasks: 29 (limit: 154341)
     Memory: 35.5M
        CPU: 436ms
     CGroup: /system.slice/prometheus.service
             └─8056 /usr/bin/prometheus

Feb 16 20:24:16 amd-gpu-machine prometheus[8056]: ts=2024-02-17T01:24:16.266Z caller=head.go:598 level=info component=tsdb msg="WAL replay completed" checkpoint_replay_duration=21.65µs wal_replay_duration=198.349µs total_replay_duration=237.319µs
Feb 16 20:24:16 amd-gpu-machine prometheus[8056]: ts=2024-02-17T01:24:16.267Z caller=main.go:850 level=info fs_type=EXT4_SUPER_MAGIC
Feb 16 20:24:16 amd-gpu-machine prometheus[8056]: ts=2024-02-17T01:24:16.267Z caller=main.go:853 level=info msg="TSDB started"
Feb 16 20:24:16 amd-gpu-machine prometheus[8056]: ts=2024-02-17T01:24:16.267Z caller=main.go:980 level=info msg="Loading configuration file" filename=/etc/prometheus/prometheus.yml
Feb 16 20:24:16 amd-gpu-machine prometheus[8056]: ts=2024-02-17T01:24:16.268Z caller=main.go:1017 level=info msg="Completed loading of configuration file" filename=/etc/prometheus/prometheus.yml totalDuration=901.686µs db_storage=650ns remote_storage=1.61µs web_handler=390ns query>
Feb 16 20:24:16 amd-gpu-machine prometheus[8056]: ts=2024-02-17T01:24:16.268Z caller=main.go:795 level=info msg="Server is ready to receive web requests."
Feb 16 20:27:44 amd-gpu-machine systemd[1]: Reloading Monitoring system and time series database...
Feb 16 20:27:44 amd-gpu-machine prometheus[8056]: ts=2024-02-17T01:27:44.486Z caller=main.go:980 level=info msg="Loading configuration file" filename=/etc/prometheus/prometheus.yml
Feb 16 20:27:44 amd-gpu-machine systemd[1]: Reloaded Monitoring system and time series database.
Feb 16 20:27:44 amd-gpu-machine prometheus[8056]: ts=2024-02-17T01:27:44.487Z caller=main.go:1017 level=info msg="Completed loading of configuration file" filename=/etc/prometheus/prometheus.yml totalDuration=525.837µs db_storage=1.22µs remote_storage=1.77µs web_handler=580ns quer>
lines 1-23/23 (END)
```