# The file is to process two inputs files (lookup table and flow log) and generate the required result in an output file
from protocol_def import protocol_dict
import csv

class TrieNode:
    def __init__(self):
        self.children = {} # children node
        self.tag_count = {} # count for one port-protocol tag and number
        self.is_end_of_combination = False
        self.port_protocol_count = 0  # count for port-protocol combinations in the Trie

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.untagged_count = 0 # total number to track untagged counts
        self.untagged_combinations = {}  # dictionary to track all untagged port-protocol combination counts

    # Insert port-protocol-tag combination
    def insert(self, port, protocol, tag):
        node = self.root

        # Reverse the port since I want to build up the trie from the unit digit -> ten digit -> and so forth, then we don't need to do padding '0' to all ports to reach five digits
        reversed_port = port[::-1] 
        # Break the port number into digits and insert each digit as a node
        for digit in str(reversed_port):
            if digit not in node.children:
                node.children[digit] = TrieNode()
            node = node.children[digit]
        
        # Insert protocol
        if protocol not in node.children:
            node.children[protocol] = TrieNode()
        node = node.children[protocol]

        # Lookup table file is generated randomly, it might get the case that is same port/protocol BUT with different tags. If it happened, I would keep the first port/protocol/tag record
        # Now, this dictionary will have only one key/value pair. Using dictionary just in case if we really want to append different tags
        # Insert or increment tag count
        if not node.tag_count:
            node.tag_count[tag] = 0

        node.is_end_of_combination = True # mark as end for each port/protocol/tag

    # Search for port-protocol pair and update the count
    def search_and_count(self, port, protocol):
        node = self.root

        # Reverse the port to search through the trie
        reversed_port = port[::-1]
        # Traverse the port digit by digit
        for digit in str(reversed_port):
            if digit in node.children:
                node = node.children[digit]
            else:
                # Port not found, mark as untagged
                self._increment_untagged_count(port, protocol)
                return
        
        # Traverse protocol
        if protocol in node.children:
            node = node.children[protocol]
            # Increment the port-protocol count
            node.port_protocol_count += 1
        else:
            # Protocol not found, mark as untagged
            self._increment_untagged_count(port, protocol)
            return

        # Count the tag if found, otherwise count as untagged
        if node.is_end_of_combination:
            for tag in node.tag_count.keys():
                node.tag_count[tag] += 1
        else:
            self._increment_untagged_count(port, protocol)

    # Increment the count for untagged port/protocol combinations
    def _increment_untagged_count(self, port, protocol):
        self.untagged_count += 1
        port_protocol = f"{port},{protocol}"
        if port_protocol not in self.untagged_combinations:
            self.untagged_combinations[port_protocol] = 0
        self.untagged_combinations[port_protocol] += 1

    # Get all tag counts by traversing the Trie
    def get_tag_counts(self, node=None, result=None):
        if result is None:
            result = {}
        if node is None:
            node = self.root
        
        # If the current node has tag, accumulate the counts
        if node.tag_count:
            for tag, count in node.tag_count.items():
                if tag not in result:
                    result[tag] = 0
                result[tag] += count
        
        # Recursively go through all children
        for child in node.children.values():
            self.get_tag_counts(child, result)
        
        return result
    
    # Get all port-protocol combination counts
    def get_port_protocol_counts(self, node=None, current_port_protocol="", result=None):
        if result is None:
            result = {}
        if node is None:
            node = self.root

        # If we are at a protocol level, store the count
        if node.port_protocol_count > 0:
            result[current_port_protocol] = node.port_protocol_count

        # Recursively go through all children
        for key, child_node in node.children.items():
            if '0' <= key <= '9':
                new_port_protocol = current_port_protocol + key
            else:
                # Hit the protocol now, reverse port back to show the correct port
                new_port_protocol = current_port_protocol[::-1] + ", " + key
            self.get_port_protocol_counts(child_node, new_port_protocol, result)
        
        return result

    # Get all untagged port-protocol counts combinations and counts
    def get_untagged_port_protocol_combinations(self):
        return self.untagged_combinations

# Helper function to read CSV files
def read_csv_file(filepath):
    with open(filepath, 'r') as file:
        return [line.strip().split(",") for line in file]

# Generate an required output file
def write_result_to_csv(trie):
    assert trie is not None, "Trie is not built up successfully."

    # Define the output CSV file path
    output_csv_file = "tag_counts_and_port_protocol_combination_counts.csv"
    # Write to CSV file
    with open(output_csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        ## 1. Write the Count of matches for each tag
        # Write header
        writer.writerow(["Tag", "Count"])
        
        # Write each tag counts
        for tag, count in trie.get_tag_counts().items():
            writer.writerow([tag, count])
        
        # Write the untagged counts
        writer.writerow(["Untagged", trie.untagged_count])

        ## 2. Write the Count of matches for each port/protocol combination
        # Write the header
        writer.writerow(["Port", "Protocol", "Count"])

        # Write the tag port-protocol counts combinations
        for port_protocol, count in trie.get_port_protocol_counts().items():
            # Split the port and protocol based on the comma
            port, protocol = port_protocol.split(", ")
            writer.writerow([port, protocol, count])

        # Write untagged port-protocol counts combinations
        for port_protocol, count in trie.get_untagged_port_protocol_combinations().items():
            # Split the port and protocol based on the comma
            port, protocol = port_protocol.split(",")
            writer.writerow([port.strip(), protocol.strip(), count])
    print(f"required counts have been successfully written to {output_csv_file}")

def main():
    trie = Trie()
    lookup_table_csv_file = "lookup_table_with_protocol_names.csv"
    flow_log_csv_file = "flow_log.csv"

    # Build the Trie by lookup table file
    csv_lines = iter(read_csv_file(lookup_table_csv_file))  # create an iterator from the csv file
    next(csv_lines)  # skip the header row
    # Insert all combinations from the lookup table into the Trie
    for line in csv_lines:
        port, protocol, tag = line[0].strip(), line[1].strip().lower(), line[2].strip().lower()
        trie.insert(port, protocol, tag)

    # Search and count the Trie by flow log file
    csv_lines2 = iter(read_csv_file(flow_log_csv_file))  # create an iterator from the csv file
    next(csv_lines2)  # skip the header row
    # Traverse the flow log file and search each dstport-protocol pair
    for line in csv_lines2:
        port, protocol = line[6].strip(), line[7].strip().lower() # only need dstport and protocol info to search
        if int(protocol) in protocol_dict.keys():
            protocol = protocol_dict[int(protocol)]
        else:
            protocol = "Unassigned"
        trie.search_and_count(port, protocol.lower())
    
    # Write the result and generate the output file
    write_result_to_csv(trie)

if __name__ == '__main__':
    main()