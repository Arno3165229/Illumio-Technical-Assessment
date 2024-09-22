# Illumio-Technical-Assessment

### Intro
* This repo is for the illumio take-home assessment
* Objective: Write a program that can parse a file containing flow log data and maps each row to a tag based on a lookup table. The program should generate an output file

### How to run
* Command (Run in terminal): 
    ```
    python generator_lookup_table.py # it will generate the lookup_table_with_protocol_names.csv
    ```
    ```
    python generator_flow_log.py # it will generate the flow_log.csv
    ```
    ```
    python processor.py # it will pass lookup_table_with_protocol_names.csv and flow_log.csv under same directory, and generate the tag_counts_and_port_protocol_combination_counts.csv
    ```

### Analysis, assumption, and testing
* protocol_def.py
    * This file is for protocol number to protocol name mapping 
    * Reference from https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml

* generator_lookup_table.py
    * This file is to randomly generate the lookup table CSV file
    * Assume to create 10 tags, starting from sv_P1 to sv_P10
    * Port range is from 0 to 65535
    * Protocol number is from 0 to 255, and protocol number from 146-252 will be seen as 'Unassigned'
    * Mapping is totally up to 10000, it is also randomly generated
    * It will also generate the header in csv file

* generator_flow_log.py
    * This file is to generate the input flow log CSV file
    * Assume the flow log is coming from one interface and record it every 5 seconds, which means each start time and end time is 5s difference
    * Assume the version is 2
    * Assume the account_id is '123456789012'
    * Assume the interface_id is 'eni-0a1b2c3d'
    * Assume packet number from 0 to 1000
    * Assume total packet sizes from 0 to 10000
    * src address and dst address should be range from 0.0.0.0 to 255.255.255.255 (IPv4)
        * It's might be not so reasonable since the protocol I generated is range from 0 to 255, which means the ip address should not IPv4 only. However, for this test, we don't really use address for hashing. For easily generated, I just used only IPv4 here
    * src port and dst port should be from 0 to 65535
    * Protocol number is from 0 to 255, and protocol number from 146-252 will be seen as 'Unassigned'
    * Other infos should follow the sample log format reference https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html
    * It will also generate the header in csv file

* processor.py
    * The file is to process two inputs files (lookup table and flow log) and generate the required result in one output file
    * Lookup table file is generated randomly, it might get the case that is same port/protocol BUT with different tags. If it happened, I would only keep the first port/protocol/tag record to get rid of double count for different tags
    * I used the Trie to build up the data structure from lookup table.
        * Compared to directly use the dictionary, when the lookup table keeps scaling up, it will have better perfomance ideally for the log file searching
            * It can search the port digit by digit from the trie structure, and make the time complexity to reach lower level -> O(L), which L is dat length for searching
        * I reversed the port to insert the node since I wanted to build up the trie from the unit digit -> ten digit -> and so forth, then we don't need to do padding '0' to all ports to reach five digits
    * For other detail, please check this python file, I have put more detailed comment there
    * Improvement
        * The one concern is I used a dictionary, untagged_combinations, to store all untagged port/protocol combinations counts. After the testing result, I found most of log file port/protocol belong to untagged. Therefore, for each searching, it might have a higher chance to go through this dictionary to increment the value. However, with the lookup table file scaling up and also the most port numbers should come from 0 to 1023 in real scenario. I think this issue will become more acceptable since most port/protocol will belong to tags and stored inside the Trie
    * Testing
        * Do the unit testing. Generating the small and fixed amout of input files and check if the result correct