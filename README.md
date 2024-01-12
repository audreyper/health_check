## Daily Health Check Script

This Python script monitors the health of a remote server by capturing and analyzing the 
output of specific commands related to disk usage, CPU performance, and RAM utilization.

### Prerequisites

Ensure that the paramiko library is installed. 

### Usage

1. Update the script with the appropriate values for host, user, and password to establish a connection with the remote server.

2. Schedule the script to run at regular intervals using a task scheduler or a job scheduling library. If you're using Linux, a suggestion for scheduling with a cron job is provided below.

3. Customize the email settings in the script, including subject, sender, recipients, and password for the email account.

4. Change the values associated with thresholds to fit your specific requirements. Modify these thresholds according to the levels that indicate potential issues for your system.

5. Execute the script to capture health metrics, generate CSV files (cpu.csv, disk.csv, ram.csv), and send an email report. Ensure the execution aligns with your scheduled intervals for consistent monitoring.

### Scheduling with Cron (Linux)

To schedule the script to run daily at 9:00 AM, you can use a cron job:

```bash
0 9 * * * /path/to/python3 /path/to/health_check_script.py
```

Replace /path/to/python3 with the path to your Python 3 interpreter and /path/to/health_check_script.py 
with the actual path to your Python script.

### Email Reports

The script generates an email report with three HTML tables summarizing the monitoring results. It includes information on disk capacity, CPU utilization, and RAM usage. 
If any thresholds are exceeded, the email subject is updated to indicate an alert. 