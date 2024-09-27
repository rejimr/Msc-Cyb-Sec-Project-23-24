import requests
import asyncio
from web3 import Web3
import json
from dotenv import load_dotenv
import os
load_dotenv()

# Connect to Blockchain
url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(url))
assert web3.is_connected(), "Sorry, not able to connect to Blockchain"
print("successfully connected to Blockchain")

# Load the contract ABI from the compiled SmartContractAICompensation.json file (build file)
with open('build/contracts/SmartContractAICompensation.json') as contractj:
    jsonContract = json.load(contractj)
    abi = jsonContract['abi']

# Details of Contract address and ABI
contractAddress = os.getenv('CONTRACTADRESS')
contract = web3.eth.contract(address=contractAddress, abi=abi)

# Details of LLM address and private key
llmAddress = os.getenv('LLMADDRESS')
llmPrivateKey = os.getenv('LLMPRIVATEKEY')



# Details of judge's address and private key
adminAddress = os.getenv('ADMINADRESS')
adminPrivateKey = os.getenv('ADMINPRIVATEKEY')

unitGasPrice = web3.eth.gas_price
numberofTokens = 0


# Function definition to send a prompt to LLaMA2 and receive a response
def sendPrompt(prompt,responseLimit, max_tokens=1, temperature=0.7):
    max_tokens = int(responseLimit)
    Max_tokensAllowed = 360
    max_tokens = min(int(responseLimit), Max_tokensAllowed)
    url = "http://localhost:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        numberofTokens = result["usage"]["completion_tokens"]
        print("number of tokesns",result["usage"]["completion_tokens"])
        return result["choices"][0]["message"]["content"],numberofTokens
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None

# Function to listen for events from client and update responses
async def eventListenerQuery():
    eventfilterQuery = contract.events.submittedQuery.create_filter(fromBlock='latest')
    eventfilterResponseFee = contract.events.printResponseFee.create_filter(fromBlock='latest')
    eventfilterRefund = contract.events.printRefund.create_filter(fromBlock='latest')
    while True:
        for event in eventfilterQuery.get_new_entries():
            userAddress = event['args']['user']
            queryId = event['args']['queryID']
            submittedQuery = event['args']['query']
            queryLength = len(submittedQuery)
            unitFee = web3.to_wei('0.001','ether')
            queryFee = queryLength * unitFee
            queryfeeinEther  = Web3.from_wei(queryFee, 'ether')
            print ("queryfee in ether is :",queryfeeinEther )
            print(f"Processing query {queryId} for user {userAddress}: {submittedQuery}")
            feesPaid = event['args']['fee']
            print(f"fees paid is ,{Web3.from_wei(feesPaid, 'ether')} Ether")
            responseCharLimit = (feesPaid - queryfeeinEther )/unitFee
            print ("responseCharLimit is :",int(responseCharLimit))

            
            # Process the query using LLaMA2
            response,numberofTokens = sendPrompt(submittedQuery,responseCharLimit-1)
            if response:
                nonce = web3.eth.get_transaction_count(llmAddress)
                responseFee = numberofTokens * unitFee
                print("response is ",response)
                
                print ("resposne fee before sending ",responseFee)
                #response = 'a'
                gasEstimate = contract.functions.updateResponse(userAddress, queryId, response,queryFee,responseFee).estimate_gas({'from': llmAddress})
                transaction = contract.functions.updateResponse(userAddress, queryId, response,queryFee,responseFee).build_transaction({
                    'from': llmAddress,
                    'nonce': nonce,
                    #'gas': 1500000,
                    'gas' :gasEstimate,
                    'gasPrice': unitGasPrice,
                })
                signedTransaction = web3.eth.account.sign_transaction(transaction, llmPrivateKey)
                transactionHash = web3.eth.send_raw_transaction(signedTransaction.rawTransaction)
                transactionReceipt = web3.eth.wait_for_transaction_receipt(transactionHash)
                print(f"Response for query {queryId} updated on blockchain for user {userAddress}.")
                print(f"Transaction hash for updating response is : {web3.to_hex(transactionHash)}")
                print("Updated the response on blockchain")
                #gasUsed = transactionReceipt.gasUsed
                gasPriceinWei = web3.eth.get_transaction(transactionHash).gasPrice
                totalgasPrice = gasPriceinWei * transactionReceipt.gasUsed
                print ("gas price in wei",gasPriceinWei)
                print ("gas used ",transactionReceipt.gasUsed)
                print("Gas Price for updating gresponse is : ",totalgasPrice)
                print("Gas Price in ether updating gresponse is: ",web3.from_wei(totalgasPrice, 'ether'),"Ether")
                print("Gas Price in USD updating gresponse  is: ",web3.from_wei(totalgasPrice, 'ether')*2500)               

                #printing the llm fee which is the total amount of query processing and response retriving
                for event in eventfilterResponseFee.get_new_entries():
                    totaLlmFee = event['args']['totaLlmFee']
                    print("Response fee in wei is ",totaLlmFee)
                    print(f"Response fee in ether is :{Web3.from_wei(totaLlmFee, 'ether')} Ether")
                    #print("Response fee is ",eventfilterResponseFee['args']['responseFee'])

                # printing the refund amount which will be refunded to user's account which is balance amount after processing the wuery and updating the response
                for event in eventfilterRefund.get_new_entries():
                    refund = event['args']['refund']
                    print("Refund amount in wei is ",refund)
                    print(f"Refund fee in ether is :{Web3.from_wei(refund, 'ether')} Ether")
                    
                   
                
            else:
                print(f"Failed to generate response for query {queryId}")

        await asyncio.sleep(5)



async def eventListenerCompensation():
    eventfilterCompensation = contract.events.requestCompensation.create_filter(fromBlock='latest')
    while True:
        for event in eventfilterCompensation.get_new_entries():
            userAddress = event['args']['user']
            queryId = event['args']['queryID']
            givenQuery = event['args']['givenQuery']
            givenResponse = event['args']['givenResponse']
            #givenResponse = "vnmvn"
            print ("Given Response",givenResponse)
            print(f"Processing compensation request for user {userAddress}: queryId {queryId}")
       

            # Process the query using LLaMA2 and verify
            responseLimit =360
            verifiedResponse = sendPrompt(givenQuery,responseLimit)
            if verifiedResponse:
                print(f"checked query and new Generated response is : {verifiedResponse}")
                
                if verifiedResponse != givenResponse:
                    # Update the response on the blockchain
                    nonce = web3.eth.get_transaction_count(adminAddress)
                    transaction = contract.functions.compensationPayment(userAddress, queryId).build_transaction({
                        'from': adminAddress,
                        'nonce': nonce,
                        'gas': 1200000,
                          
                    })
                    signedTransaction = web3.eth.account.sign_transaction(transaction, adminPrivateKey)
                    transactionHash = web3.eth.send_raw_transaction(signedTransaction.rawTransaction)
                    transactionReceipt = web3.eth.wait_for_transaction_receipt(transactionHash)
                    print(f"Compensation for query {queryId} processed for user {userAddress}.")
                    print(f"Transaction hash for updating compensation is : {web3.to_hex(transactionHash)}")
                    print("Updated the compensation on blockchain")
                    #gasUsed = transactionReceipt.gasUsed
                    gasPriceinWei = web3.eth.get_transaction(transactionHash).gasPrice
                    print ("gas price in wei",gasPriceinWei)
                    print ("gas used ",transactionReceipt.gasUsed)
                    # gas price in ether = gas price in gwei * gas used * conversion factor
                    totalgasPrice = gasPriceinWei * transactionReceipt.gasUsed
                    print("Gas Price for updating compensation is : ",totalgasPrice)
                    print("Gas Price in ether updating compensation is: ",web3.from_wei(totalgasPrice, 'ether'),"Ether")
                    print("Gas Price in USD updating compensation  is: ",web3.from_wei(totalgasPrice, 'ether')*2500)
                else:
                    print("Response is correct, compensation request failed")
            else:
                print(f"Failed to generate verification response for query {queryId}")

        await asyncio.sleep(10)
    

    

if __name__ == "__main__":
    # Run both event listeners concurrently
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(eventListenerQuery()),
        loop.create_task(eventListenerCompensation())
    ]
    loop.run_until_complete(asyncio.gather(*tasks))





    
