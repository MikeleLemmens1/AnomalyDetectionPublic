import pandas as pd
import ast
import csv
import os
import sys 

root = os.path.abspath(".")
sys.path.append(root)

from func.dep2pyodbc import dep2connection

# Connection with the database
channel_crh = dep2connection("CRH")
cursor = channel_crh.cursor()

def getBits(bits, start, length):
    """
    Extract a slice of bits from a byte string.
    
    Args:
        bits (bytes): The byte string to extract bits from.
        start (int): The starting position of the slice.
        length (int): The length of the slice to extract.
    
    Returns:
        str: A string representation of the extracted bits.
    """
    # Convert the byte string to a normal string
    bits_str = ''.join(f'{byte:08b}' for byte in bits)
    
    # Extract the slice of bits from the string
    return bits_str[start:start + length]

def GetValueFromBinaryString(bits, start, length):
    """
    Convert a slice of bits from a byte string into an integer value.
    
    Args:
        bits (bytes): The byte string to extract bits from.
        start (int): The starting position of the slice.
        length (int): The length of the slice to extract.
    
    Returns:
        int: The integer value of the extracted binary string.
    """
    return int(getBits(bits, start, length), 2)

def decode_val_with_bitshift(data, offset, length=0xf):
    """
    Decode a value from the given data by applying a bitshift operation.
    
    Args:
        data (int): The data to decode the value from.
        offset (int): The offset position to apply the bitshift.
        length (int, optional): The length of the mask to apply. Defaults to 0xf.
    
    Returns:
        int: The decoded value.
    """
    return (data >> offset) & length

def decode_baq(data):
    """
    Decode the BAQ data from the provided byte string into a structured format.
    
    Args:
        data (bytes): The byte data to decode.
    
    Returns:
        list: A list of dictionaries containing the decoded data for each item.
    """
    items_amount = 60
    NUMBER_OF_BYTES = 8
    BITVECTOR_BYTE_SIZE = 4
    items = []

    for item_index in range(items_amount):
        offset = item_index * 8
        
        item_bytes = data[offset:offset + NUMBER_OF_BYTES]

        # Split the bytes into normative and ipsative parts
        normative_bytes = item_bytes[:BITVECTOR_BYTE_SIZE]
        ipsative_bytes = item_bytes[BITVECTOR_BYTE_SIZE:]

        normative = int.from_bytes(normative_bytes, byteorder='little')
        ipsative = int.from_bytes(ipsative_bytes, byteorder='little')

        normative_vals = []
        ipsative_vals = []
        
        # Decode the normative values
        item_id = decode_val_with_bitshift(normative, 0, 0x3f)
        first_val = decode_val_with_bitshift(normative, 6)
        second_val = decode_val_with_bitshift(normative, 10)
        third_val = decode_val_with_bitshift(normative, 14)
        fourth_val = decode_val_with_bitshift(normative, 18)
        fifth_val = decode_val_with_bitshift(normative, 22)

        normative_vals.append({
            "item_id": item_id,
            "first_val": first_val,
            "second_val": second_val,
            "third_val": third_val,
            "fourth_val": fourth_val,
            "fifth_val": fifth_val
        })
        
        # Decode the ipsative values
        item_id = (ipsative >> 0) & 0x3F
        first_val = decode_val_with_bitshift(ipsative, 6)
        second_val = decode_val_with_bitshift(ipsative, 10)
        third_val = decode_val_with_bitshift(ipsative, 14)
        fourth_val = decode_val_with_bitshift(ipsative, 18)
        fifth_val = decode_val_with_bitshift(ipsative, 22)

        ipsative_vals.append({
            "item_id": item_id,
            "first_val": first_val,
            "second_val": second_val,
            "third_val": third_val,
            "fourth_val": fourth_val,
            "fifth_val": fifth_val
        })

        items.append({"normative_vals": normative_vals, "ipsative_vals": ipsative_vals})

    return items

# Fetch data from the database
coded_BAQ = pd.read_sql("SELECT * FROM CandidateResultBA51", channel_crh)

# Define output file and batch processing settings
output_file = 'decoderen/raw_data/decoded_baq.csv'
batch_size = 1000
buffer = []
count = 0

# Write the header only once
with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=[
        'CandidateID', 'InstanceID', 
        'itemId_norm', 'norm_1', 'norm_2', 'norm_3', 'norm_4', 'norm_5',
        'itemId_ips', 'ips_1', 'ips_2', 'ips_3', 'ips_4', 'ips_5'
    ])
    writer.writeheader()

# Process data in batches
for index, row in coded_BAQ.iterrows():
    byte_data = row['Data']
    data = decode_baq(byte_data)

    if index % 25000 == 0:
        print("progress", index)

    for item in data:
        normative = item['normative_vals'][0]
        ipsative = item['ipsative_vals'][0]

        # Flatten the decoded data
        flattened_row = {
            'CandidateID': row['CandidateID'],
            'InstanceID': row['InstanceID'],
            'itemId_norm': normative['item_id'],
            'norm_1': normative['first_val'],
            'norm_2': normative['second_val'],
            'norm_3': normative['third_val'],
            'norm_4': normative['fourth_val'],
            'norm_5': normative['fifth_val'],
            'itemId_ips': ipsative['item_id'],
            'ips_1': ipsative['first_val'],
            'ips_2': ipsative['second_val'],
            'ips_3': ipsative['third_val'],
            'ips_4': ipsative['fourth_val'],
            'ips_5': ipsative['fifth_val'],
        }

        buffer.append(flattened_row)

        # If the buffer is full, write to the CSV file
        if len(buffer) >= batch_size:
            with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=flattened_row.keys())
                writer.writerows(buffer)
                count += 1
            buffer = []

# Write any remaining rows
if buffer:
    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=buffer[0].keys())
        writer.writerows(buffer)
