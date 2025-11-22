"""
This script uses a Llama 3.1 8B model to generate a summary of an example test and defines the function to do so. 

This script can also be ran as a module that includes the following functions: 
    * get_summary_from_dict: generates an instance summary
"""

import os
import datetime
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

def get_summary_from_dict(instance, HF_TOKEN):
    """
    This function generates an instance summary. 

    This function uses prompt engineering to have a Llama 3.1 8B model generate a summary of up to 200 words.
    The model uses an API which requires a Hugging Face token 
    
    Parameters
    ----------
    instance : dict
        the test instance passed as a dict

    hf_token : str

    Raises
    ------
    [InferenceTimeoutError]
    If the model is unavailable or the request times out.

    HTTPError
    If the request fails with an HTTP error status code other than HTTP 503.

    """

    client = InferenceClient(
    "NousResearch/Hermes-3-Llama-3.1-8B",
    token=HF_TOKEN,
    )

    prompt=f'''
    You are an assistent that needs to transform data into a summary.
    I have a dictionary of an item that contains values for several attributes of the test instance. 
    Can you generate a summary of 100 words where some random attributes are chosen from this dictionary?
    This is the dictionary: {instance}

    There are some rules you need to follow:
    - When a certain attribute is 1 = True or 0 = False, don't mention this literally.
    - The SameAnswer field represents the frequency of the answer that was most given in a test instance
    - Lof, iForest, COPOD, ECOD, ABOD, PyodEnsemble, DBSCAN, TooFast, TooSlow and Neighbours are methods returning 1 or 0. 1 meaning this detectionmethod considered the test to be an anomaly, 0 meaning it did not. 
    - Don't mention values in the form of "Gender_male" or "Qualification_Unknown", interpret the values without the prefix up until the underscore
    - Interpret the language by the first 2 characters of the value. e.g. 'en-INT' should be english
    - The unit of TimeSpent is seconds, but represent it in an easy to read format (3660s must be written as 1 hour and 10 seconds). 
    - Do not mention None values,  missing values or detection methods that were not applied. 
    - The AnomalyScore signifies the percentages of detection methods that flagged this test as an anomaly. It is used to determine whether the test is a significant outlier.  
    - IsAnomaly returns 1 or 0, with 1 meaning the AnomalyScore determined the test to be an anomaly, 0 meaning it did not. 
    - Do not mention the actual names "AnomalyScore", "IsAnomaly", "TooFast", "TooSlow". 
    - Use a maximum of six sentences. 
    - Use a professional tone. 

    Remember to only give a summary, not a dialogue. Don't make up false facts, and you cannot use an informal tone. 
    '''
    final = ""
    for message in client.chat_completion(
    	messages=[{"role": "user", "content": prompt}],
    	max_tokens=500,
    	stream=True,
      temperature=1):
      
      final = final + message.choices[0].delta.content
    return final
    

dict = {'Test': 'FCA',
 'CandidateKey': 544,
 'TimeSpent': 18.0,
 'SameAnswer': 46.66666666666666,
 'TooFast': False,
 'TooSlow': True,
 'DBSCAN': True,
 'Neighbours': False,
 'Date': datetime.date(2022, 9, 8),
 'Organisation': 'B2BABE21-1705-4750-AE99-8D1316755876',
 'ChosenLanguage': 'en-INT',
 'ChosenGender': 'Gender_Female',
 'Gender': 'Gender_Female',
 'Qualification': 'Qualification_Unknown'}

load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

print(get_summary_from_dict(dict,HF_TOKEN))