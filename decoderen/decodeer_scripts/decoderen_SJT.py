import pandas as pd
import ast
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

def decodeSjtRow(data, index):
    """
    Decode a single row of SJT data.
    
    Args:
        data (bytes): The byte data to decode.
        index (int): The index of the row to decode.
    
    Returns:
        dict: A dictionary containing the decoded values for the row.
    """
    offset = 16 * 4 * index
    situationId = GetValueFromBinaryString(data, offset, 20)
    sequenceIds = [
        GetValueFromBinaryString(data, offset + 20, 4),
        GetValueFromBinaryString(data, offset + 24, 4),
        GetValueFromBinaryString(data, offset + 28, 4)
    ]
    # Handle sequence ID values of 0
    sequenceIds = [1 if seq == 0 else seq for seq in sequenceIds]
    
    answers = [
        GetValueFromBinaryString(data, offset + 32, 3),
        GetValueFromBinaryString(data, offset + 35, 3),
        GetValueFromBinaryString(data, offset + 38, 3)
    ]
    scores = [
        GetValueFromBinaryString(data, offset + 41, 3),
        GetValueFromBinaryString(data, offset + 44, 3),
        GetValueFromBinaryString(data, offset + 47, 3)
    ]
    timeSpent = GetValueFromBinaryString(data, offset + 50, 14)
    
    return {
        "situationId": situationId,
        "sequenceIds": sequenceIds,
        "answers": answers,
        "scores": scores,
        "timeSpent": timeSpent
    }

def decodeSjt(data):
    """
    Decode the entire SJT dataset from binary data.
    
    Args:
        data (bytes): The byte data to decode.
    
    Returns:
        list: A list of dictionaries, each containing decoded information for a row.
    """
    items = len(data) // (16 * 4)
    data_ = []
    for i in range(items + 1):
        data_.append(decodeSjtRow(data, i))
    return data_

# Fetch data from the database
coded_sjt = pd.read_sql("SELECT * FROM CandidateResultSJT", channel_crh)

# List to store all flattened data
all_flattened_data = []

# Loop through each row in the DataFrame
for index, row in coded_sjt.iterrows():
    # Decode the 'Data' column
    byte_data = row['Data']

    if index % 500 == 0:
        print("SJT", index)
    
    # Decode the data
    data = decodeSjt(byte_data)
    
    # Flatten the decoded data
    for item in data:
        flat_item = {
            'CandidateID': row['CandidateID'],
            'InstanceID': row['InstanceID'],
            'itemId': item['situationId'],
            'sequenceId1': item['sequenceIds'][0],
            'sequenceId2': item['sequenceIds'][1],
            'sequenceId3': item['sequenceIds'][2],
            'answer1': item['answers'][0],
            'answer2': item['answers'][1],
            'answer3': item['answers'][2],
            'score1': item['scores'][0],
            'score2': item['scores'][1],
            'score3': item['scores'][2],
            'timeSpent': item['timeSpent']
        }
        all_flattened_data.append(flat_item)

# Create a new DataFrame from all flattened data
final_df = pd.DataFrame(all_flattened_data)

# Save the DataFrame to a CSV file
final_df.to_csv('decoderen/raw_data/decoded_sjt.csv')
