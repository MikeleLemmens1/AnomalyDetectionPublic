import json
import subprocess
import pandas as pd
import os
import sys
import platform
import time

root = os.path.abspath(".")
sys.path.append(root)

from func.dep2pyodbc import dep2connection

DECODER_PATH = os.path.join(os.getcwd(),"decoderen","DecoderApp", "DecoderApp", "bin", "release", "net8.0", "publish", "DecoderApp.exe")
if platform.system() == "Linux":
  DECODER_PATH = os.path.join(os.getcwd(),"decoderen","DecoderApp", "DecoderApp", "bin", "release", "linux", "out", "DecoderApp")
CSV_FOLDER = os.path.join(os.getcwd(),"decoderen","raw_data")
OUTPUT_PATH = os.path.join(os.getcwd(),"decoderen","raw_data","decoded_fca.csv")
STRINGS_OUTPUT_PATH= os.path.join(os.getcwd(),"decoderen","raw_data","bytestrings_fca.csv")

# PATH_FAILED_DECODINGS = r".\decoderen\csv\fca_failed_decodings.csv"

channel = dep2connection("CRH")
cursor = channel.cursor()

def binarystrings_to_csv():
  sql = """
  SELECT CandidateID, c.InstanceID, Data, InstrumentClassID 
  FROM CandidateResultFCA as cfa JOIN Candidate as c ON cfa.CandidateID = c.ID AND cfa.InstanceID = c.InstanceID
  """
  rows = cursor.execute(sql).fetchall()

  columns = [
    "CandidateId",
    "InstanceId",
    "Data",
    "InstrumentClassId",
    ]
  
  df_failed = pd.DataFrame(columns=["InstrumentClassId", "CandidateId", "InstanceId"])

  decoded_test_results = pd.DataFrame(columns=columns)
  
  tests_decoded = 0
  start_time = time.time()
  status_info_amount = 5000

  candidates = []
  instances = []
  bytestrings = []
  instruments = []

  df = pd.DataFrame(columns=columns)
  for row in rows:
    try:
      candidateId = row[0]
      instanceId = row[1]
      bytestring = row[2].hex()
      instrumentClassId = row[3]
      candidates.append(candidateId)
      instances.append(instanceId)
      bytestrings.append(bytestring)
      instruments.append(instrumentClassId)

      tests_decoded += 1
    except Exception as ke:
      df_failed.loc[tests_decoded] = [candidateId, instanceId, instrumentClassId]
      # df_failed.to_csv(PATH_FAILED_DECODINGS, index=False, header=True)
      # print(f"tests_decoded before error: {tests_decoded}")
      print(f"Failed decoding {tests_decoded}; Candidate: {row[1]}, InstanceId: {row[2]}")
      # print(ke)

  df = pd.DataFrame({
    "CandidateId" : candidates,
    "InstanceId" : instances,
    "Data" : bytestrings,
    "InstrumentClassId" : instruments
  })

  if not os.path.exists(CSV_FOLDER):
    os.mkdir(CSV_FOLDER)
  df.to_csv(STRINGS_OUTPUT_PATH, index=False, header=True)
  
  cmd = DECODER_PATH
  # TODO: paden in MainModule.vb robuust maken
  subprocess.Popen([cmd, "FCA", CSV_FOLDER],stdout=subprocess.PIPE)

  # df_failed.to_csv(PATH_FAILED_DECODINGS, index=False, header=True)

binarystrings_to_csv()
