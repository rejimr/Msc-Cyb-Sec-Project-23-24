from dotenv import load_dotenv
import os
import Client 
load_dotenv()

# test the submit query function in client application
userAddress=os.getenv('CLIENTADDRESS')
from Client.client import submitQuery,compensationRequest,getValue
def test_submitQuery():
    print ("testing submit query function")
    submitQuery("testing query",1)

#test the compensation requet function in client applciation
def test_compesationRequest():
    print("testing compensation function")
    compensationRequest(userAddress,1)

# testing the function to retrive values from smart contract in client applciation
def test_getvalue():
    print("testing getValue function")
    queryId = 1 
    value= getValue(userAddress,queryId) # user address was stored on .env variable
    print("value in getValue is ",value)

if __name__  =="__main__":
    test_submitQuery()
    test_compesationRequest()
    test_getvalue()
