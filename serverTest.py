from dotenv import load_dotenv
import os
import Server 
load_dotenv()
import tracemalloc
tracemalloc.start()
import json
from web3 import Web3
import time
import traceback

from Server.server import sendPrompt,eventListenerQuery,eventListenerCompensation
import asyncio


#testing the  funcion to process teh resposne from LLM in server applciation
async def test_sendPrompt():
    print("testing sendPrompt fucntion")
    query = "what is the capital of Italy?"
    responseLimit =100
    response,tokens =sendPrompt(query,responseLimit)
    print("Resposne received is ",response)
    print("tokens used is",tokens)

    try:
        response, tokens = await sendPrompt(query, responseLimit)
        print(f"Response received: {response}")
        print(f"Tokens used: {tokens}")
        assert response, "Response should not be empty"
        assert tokens > 0, "Tokens should be greater than 0"
    except Exception as e:
        print(f"Error in sendPrompt: {e}")


#testing the event listener for getting the query from smart contract 
async def test_eventListenerQuery():
    print("testing evet listener query function")
    print ("this will run for 40 sec , submit a query through client interface")

    try:
        await asyncio.wait_for(eventListenerQuery(), timeout=30)
    except asyncio.TimeoutError:
        print("eventListenerQuery test completed after 30 seconds.")
    except Exception as e:
        print(f"Error in eventListenerQuery: {e}")
    

# testing the compensation request  query details event listner, here verification of resposne is happening
async def test_eventListenerCompensation():
    print("testing evet listener compensation function")
    print ("this will run for 40 sec , submit a query through client interface")

    try:
        await asyncio.wait_for(eventListenerCompensation(), timeout=30)
    except asyncio.TimeoutError:
        print("eventListenerCompensation test completed after 30 seconds.")
    except Exception as e:
        print(f"Error in eventListenerCompensation: {e}")

async def runTests():
    await test_sendPrompt()
    await asyncio.gather(
        test_eventListenerQuery(),
        test_eventListenerCompensation()
    )
if __name__  =="__main__":
    asyncio.run(runTests())

