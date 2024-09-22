# This file is to generate the input flow log file
# Assume the flow log is coming from one interface and record it every 5 seconds
import csv
import random
import os

# Constants
FILE_SIZE_LIMIT = 10 * 1024 * 1024  # Up to 10 MB based on the requirement
output_file = 'flow_log.csv'


# Function to generate random IP addresses
def random_ip():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))

# Function to generate random flow log records
def generate_flow_log_record(start_time):
    version = 2 # assume version 2
    account_id = '123456789012' # assume same account_id
    interface_id = 'eni-0a1b2c3d' # assume all flow coming from the same interface
    srcaddr = random_ip()
    dstaddr = random_ip()
    srcport = random.randint(0, 65535)
    dstport = random.randint(0, 65535)
    protocol = random.randint(0, 255)
    packets = random.randint(0, 1000) # assume packet number from 0 to 1000
    bytes_sent = random.randint(0, 10000) # assume total packet sizes from 0 to 10000
    end_time = start_time + 5  # ensure the end time is 5 units greater than start time
    action = random.choice(['ACCEPT', 'REJECT'])
    log_status = random.choice(['OK', 'NODATA', 'SKIPDATA'])
    return [version, account_id, interface_id, srcaddr, dstaddr, srcport, dstport, protocol, packets, bytes_sent, start_time, end_time, action, log_status]


# Generate and write flow log CSV until file reaches file size
def write_to_csv():
    file_size = random.randint(1, FILE_SIZE_LIMIT)  # randomly choose data size < 10 MB

    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['version', 'account-id', 'interface-id', 'srcaddr', 'dstaddr', 'srcport', 'dstport', 'protocol', 'packets', 'bytes', 'start_time', 'end_time', 'action', 'log-status']
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        
        start_time = 0  # initialize start time
        
        cur_file_size = 0 # current file size

        while cur_file_size < file_size:
            record = generate_flow_log_record(start_time)
            writer.writerow(record)
            
            start_time += 5  # increment start time by 5 for each record
            cur_file_size = os.path.getsize(output_file)


if __name__ == '__main__':
    write_to_csv()
    print(f'Flow log file "{output_file}" generated successfully.')