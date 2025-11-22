import pandas as pd
import string
import ast

import os
import sys 

# Adding the root directory to the system path
root = os.path.abspath(".")
sys.path.append(root)

from func.dep2pyodbc import dep2connection

# Establishing connection with the database
channel_crh = dep2connection("CRH")
cursor = channel_crh.cursor()

def getBits(bits, start, length):
    """
    Extracts a specific slice of bits from a byte string.

    Parameters:
    bits (bytes): The byte string to extract bits from.
    start (int): The starting bit position.
    length (int): The number of bits to extract.

    Returns:
    str: The extracted bits as a binary string.
    """
    # Convert the byte string to a normal string
    bits_str = ''.join(f'{byte:08b}' for byte in bits)
    
    # Extract the slice of bits from the string
    return bits_str[start:start + length]

def GetValueFromBinaryString(bits, start, length):
    """
    Converts a specific slice of bits from a binary string to an integer.

    Parameters:
    bits (bytes): The byte string to extract and convert.
    start (int): The starting bit position.
    length (int): The number of bits to extract.

    Returns:
    int: The integer value of the extracted bits.
    """
    return int(getBits(bits, start, length), 2)

def decode_val_with_bitshift(data, offset, length=0xf):
    """
    Decodes a value from binary data using bit shifting and masking.

    Parameters:
    data (int): The integer representation of the binary data.
    offset (int): The bit offset to start decoding from.
    length (int): The mask to apply for extracting the value. Default is 0xf.

    Returns:
    int: The decoded value.
    """
    return (data >> offset) & length

def decode_paq2018(data):
    """
    Decodes the PAQ2018 data format into readable values.

    Parameters:
    data (bytes): The raw binary data to decode.

    Returns:
    list: A list of dictionaries containing the decoded data fields:
          - left_statement (str): The left statement.
          - right_statement (str): The right statement.
          - isInversed (int): Whether the statement is inversed (1) or not (0).
          - anwser_val (int): The answer value.
    """
    num_bytes = 12

    # Determine the number of items to decode
    num_items = len(data) // num_bytes

    decoded = []
    
    for item in range(num_items + 1):
        pos = item * num_bytes
                
        item_bytes = data[pos:pos + num_bytes]

        # Convert the byte slice into an integer
        item_data = int.from_bytes(item_bytes, byteorder='little')

        # Decode the left statement
        first_letter = decode_val_with_bitshift(item_data, 0, 0x1f)
        second_letter = decode_val_with_bitshift(item_data, 5, 0x1f)
        third_letter = decode_val_with_bitshift(item_data, 10, 0x1f)
        
        left_statement = (
            string.ascii_uppercase[first_letter-1] + 
            string.ascii_uppercase[second_letter-1] +
            string.ascii_uppercase[third_letter-1] +
            "_" + str(decode_val_with_bitshift(item_data, 15, 0x7f))
        )

        # Decode the right statement
        first_letter = decode_val_with_bitshift(item_data, 32, 0x1f)
        second_letter = decode_val_with_bitshift(item_data, 37, 0x1f)
        third_letter = decode_val_with_bitshift(item_data, 42, 0x1f)

        right_statement = (
            string.ascii_uppercase[first_letter-1] + 
            string.ascii_uppercase[second_letter-1] +
            string.ascii_uppercase[third_letter-1] +
            "_" + str(decode_val_with_bitshift(item_data, 47, 0x7f))
        )
              
        # Decode additional fields
        isInversed = decode_val_with_bitshift(item_data, 64, 0x1)
        anwser_val = decode_val_with_bitshift(item_data, 65, 0x7)

        # Append decoded item to the list
        decoded.append({
            "left_statement": left_statement,
            "right_statement": right_statement,
            "isInversed": isInversed,
            "anwser_val": anwser_val
        })

    return decoded

# Query the database to get PAQ data
coded_PAQ = pd.read_sql("SELECT * FROM CandidateResultPAQ", channel_crh)

# List to store all flattened decoded data
all_flattened_data = []

# Loop through each row in the DataFrame
for index, row in coded_PAQ.iterrows():
    # Decode the 'Data' column
    byte_data = row['Data']

    # Print progress every 10,000 rows
    if index % 10_000 == 0:
        print(index)
    
    # Decode the data
    data = decode_paq2018(byte_data)
    
    # Flatten the decoded data
    for item in data:
        flat_item = {
            'CandidateID': row['CandidateID'],
            'InstanceID': row['InstanceID'],
            'left_statement': item['left_statement'],
            'right_statement': item['right_statement'],
            'anwser_val': item['anwser_val'],
        }
        all_flattened_data.append(flat_item)

# Create a new DataFrame from all flattened data
final_df = pd.DataFrame(all_flattened_data)

# Save the flattened data to a CSV file
final_df.to_csv('decoderen/raw_data/decoded_paq.csv')
