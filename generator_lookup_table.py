# This file is to randomly generate the lookup table CSV file
import csv
import random
from protocol_def import protocol_dict

# Constants
MAX_MAPPINGS = 10000 # up to 10000 mappings based on the requirement
PORT_RANGE = (0, 65535) # port range from 0 to 65535
PROTOCOL_RANGE = (0, 255) # protocol number range from 0 to 255
TAGS = [f"sv_P{i}" for i in range(1, 11)]  # assume to create 10 tags, starting from sv_P1 to sv_P10

# Function to generate random mappings with protocol names
def generate_random_mappings_with_protocol_names(num_mappings):
    mappings = []
    for _ in range(num_mappings):
        port = random.randint(*PORT_RANGE)
        protocol_number = random.randint(*PROTOCOL_RANGE)
        protocol_name = protocol_dict.get(protocol_number, "Unassigned")  # protocol number 146-252 is not in protocol dict, so just name 'Unassigned"
        tag = random.choice(TAGS)
        mappings.append([port, protocol_name, tag])
    return mappings


# Function to write the mappings to a CSV file
def write_to_csv(filename, mappings):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['dstport', 'protocol', 'tag'])  # Header
        writer.writerows(mappings)

# Generate and save the CSV
if __name__ == "__main__":
    num_mappings = random.randint(1, MAX_MAPPINGS)  # Randomly choose how many mappings to generate
    mappings = generate_random_mappings_with_protocol_names(num_mappings)
    write_to_csv('lookup_table_with_protocol_names.csv', mappings)
    print(f"{num_mappings} mappings have been generated and written to 'lookup_table_with_protocol_names.csv'.")