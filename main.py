import paramiko
import smtplib
from email.mime.text import MIMEText
import csv

host = 'x.x.x.x'
user = 'some user'
password = 'some password'

cmd_disk = 'df -h'
cmd_cpu = 'mpstat'
cmd_ram = 'free -h'

# Connects to remote server and capture 3 command's output
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=host, username=user, password=password)

stdin, stdout, stderr = ssh.exec_command(cmd_disk)
disk_output = stdout.readlines()
stdin, stdout, stderr = ssh.exec_command(cmd_cpu)
cpu_output = stdout.readlines()
stdin, stdout, stderr = ssh.exec_command(cmd_ram)
ram_output = stdout.readlines()

# Creates csv file for cpu monitoring 
with open('cpu.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    hostname = None
    for index, line in enumerate(cpu_output):
          cpu_row = line.strip().split()
          # Grabs hostname value and creates rows 
          if index == 0:
              hostname = cpu_row[2].strip('()') 
          if index == 2:
               cpu_header = [' ', cpu_row[3], cpu_row[5]]
               csv_writer.writerow(cpu_header)
          if index == 3:
               cpu_sec_row = [hostname, cpu_row[3], cpu_row[5]]
               csv_writer.writerow(cpu_sec_row)

# Creates csv file for disk monitoring
with open('disk.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    for index, line in enumerate(disk_output):
        disk_row = line.strip().split()
        if index == 0:
            disk_row = [''] + disk_row[:-2] + [' '.join(disk_row[-2:])]
        else:
            disk_row = [hostname] + disk_row
        csv_writer.writerow(disk_row)
      
# Creates csv file for RAM monitoring     
with open('ram.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    for index, line in enumerate(ram_output):
          ram_row = line.strip().split()
          if index == 0:
               ram_header = [' ', ' ', ram_row[0], ram_row[1], ram_row[5]]
               csv_writer.writerow(ram_header)
          if index == 1:
               ram_first_row = [hostname, ram_row[0], ram_row[1], ram_row[2], ram_row[5]]
               csv_writer.writerow(ram_first_row)
          if index == 2:
               ram_sec_row = [hostname,ram_row[0], ram_row[1], ram_row[2], 'N/A']
               csv_writer.writerow(ram_sec_row)

ssh.close()

# Constructs email
subject = 'Health Check Report: Everything Looks Good'
body = ''
sender = 'some email address'
recipients = ['emai address', 'email address']
password = 'password for app password gmail'

disk_path = 'disk.csv'
cpu_path = 'cpu.csv'
ram_path = 'ram.csv'

def send_email(subject, body, sender, recipients, password, disk_path, cpu_path, ram_path) :
    
    alert_subject = 'Health Check Alert: Threshold Reached'

    # Creates reader object for disk.csv
    with open(disk_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)
        disk_data = [row for row in csv_reader if row[1] != 'tmpfs']

    # Creates html table and adds header for disk monitoring
    disk_html_table = '<table border="1" cellspacing="0" cellpadding="5"><caption>Disk Monitoring</caption>'
    disk_html_table += '<tr>{}</tr>'.format(''.join(f'<th>{header_item}</th>' for header_item in header))
    
    for row_disk in disk_data:
        percentage = float(row_disk[5].strip('%'))
        # Adds red to cell if threshold reached
        if percentage > 80:
            row_disk[5] = f'<span style="color: red;">{row_disk[4]}</span>'
            subject = alert_subject
            body = 'Threshold Reached: Disk Capacity. '
        # Adds rows to table
        disk_html_table += '<tr>{}</tr>'.format(''.join(f'<td>{cell}</td>' for cell in row_disk))

     # Creates reader object for cpu.csv
    with open(cpu_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)
        data = [row for row in csv_reader]

    # Creates html table and adds header
    cpu_html_table = '<table border="1" cellspacing="0" cellpadding="5"><caption>CPU Monitoring</caption>'   
    cpu_html_table += '<tr>{}</tr>'.format(''.join(f'<th>{header_item}</th>' for header_item in header))
    
    for row_cpu in data:
        # Adds red to cell if threshold reached
            if float(row_cpu[1]) > 0.80:
                row_cpu[1] = f'<span style="color: red;">{row_cpu[1]}</span>'
                subject = alert_subject
                body += 'Threshold for Reached: CPU utilization. '
        # Adds rows to table
    cpu_html_table += '<tr>{}</tr>'.format(''.join(f'<td>{cell}</td>' for cell in row_cpu))


        # Creates reader object for ram monitoring
    with open(ram_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)
        ram_data = [row for row in csv_reader]
   
    # Creates html table and adding header
    ram_html_table = '<table border="1" cellspacing="0" cellpadding="5"><caption>RAM Monitoring</caption>'
    ram_html_table += '<tr>{}</tr>'.format(''.join(f'<th>{header_item}</th>' for header_item in header))    

    converted_number = ''.join(filter(str.isdigit, ram_data[0][4]))
    # Adds red to cell if threshold reached
    if float(converted_number) > 1300:
        ram_data[0][4] = f'<span style="color: red;">{ram_data[0][4]}</span>'
        subject = alert_subject
        body += 'Threshold Reached: RAM utilization.'

    # Adds rows to table
    ram_html_table += '<tr>{}</tr>'.format(''.join(f'<td>{cell}</td>' for cell in ram_data[0]))
    ram_html_table += '<tr>{}</tr>'.format(''.join(f'<td>{cell}</td>' for cell in ram_data[1]))

            
    # Creates email's body
    msg = MIMEText(f'{body}<br><br>'
                   f'{disk_html_table}<br>'
                   f'<table style="margin-left: auto; margin-right: auto;"{cpu_html_table}<br></table>'
                   f'<table style="margin-left: auto; margin-right: auto;"{ram_html_table}<br></table>'\
                    ,'html')
    

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    
    # Sends email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")


if __name__ == "__main__":
    # Calls the main function to send email
    send_email(subject, body, sender, recipients, password, disk_path, cpu_path, ram_path)