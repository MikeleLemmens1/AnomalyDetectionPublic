from func.dep2pyodbc import dep2connection
import pandas as pd
import ast
import os
import sys

root = os.path.abspath(".")
sys.path.append(root)


# Connection with the database
channel_crh = dep2connection("CRH")
cursor = channel_crh.cursor()


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


def decode_mdqn_regulation(data):
    """
    Decode MDQN regulation data into a structured format.

    Args:
        data (bytes): The byte data to decode.

    Returns:
        list: A list of dictionaries containing decoded values for each item.
    """
    num_items = 30
    num_bytes = 8
    BITVECTOR_BYTE_SIZE = 4
    decoded = []

    # Loop through each item and decode
    for item_ind in range(num_items):
        offset = item_ind * num_bytes
        item_bytes = data[offset:offset + num_bytes]

        # Split the bytes into normative and decode
        normative_bytes = item_bytes[:BITVECTOR_BYTE_SIZE]
        normative = int.from_bytes(normative_bytes, byteorder='little')

        # Extract values by applying bitshift
        item_id = decode_val_with_bitshift(normative, 0, 0x3F)
        first = decode_val_with_bitshift(normative, 6, 0x7)
        second = decode_val_with_bitshift(normative, 9, 0x7)
        third = decode_val_with_bitshift(normative, 12, 0x7)
        fourth = decode_val_with_bitshift(normative, 15, 0x7)
        fifth = decode_val_with_bitshift(normative, 18, 0x7)
        sixth = decode_val_with_bitshift(normative, 21, 0x7)

        # Append decoded item to list
        decoded.append({
            "item_id": item_id,
            "first_val": first,
            "second_val": second,
            "third_val": third,
            "fourth_val": fourth,
            "fifth_val": fifth,
            "sixth_val": sixth
        })

    return decoded


# Fetch the MDQN regulation data from the database
coded_mdq = pd.read_sql("SELECT * FROM CandidateResultMotivation", channel_crh)

# List to store all flattened data
all_flattened_data = []

# Loop through each row in the DataFrame
for index, row in coded_mdq.iterrows():
    # Decode the 'Data' column
    byte_data = row['Data']
    
    if index % 5000 == 0:
        print("progress", index)

    # Decodeer de data
    data = decode_mdqn_regulation(byte_data)

    # Flatten the decoded data into a simple structure
    for item in data:
        flat_item = {
            'CandidateID': row['CandidateID'],
            'InstanceID': row['InstanceID'],
            'itemId': item['item_id'],
            'first_val': item['first_val'],
            'second_val': item['second_val'],
            'third_val': item['third_val'],
            'fourth_val': item['fourth_val'],
            'fifth_val': item['fifth_val'],
            'sixth_val': item['sixth_val'],
        }
        all_flattened_data.append(flat_item)

# Create a DataFrame from all flattened data
final_df = pd.DataFrame(all_flattened_data)

# Save the flattened data to a CSV file
final_df.to_csv('decoderen/raw_data/decoded_mdq.csv')

# Print the final DataFrame
print(final_df)
