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

# Details of Contract address and ABI ,contrat address is stored in .env file
contractAddress = os.getenv('CONTRACTADRESS')
contract = web3.eth.contract(address=contractAddress, abi=abi)

# Details of LLM address and private key stored in .env file
llmAddress = os.getenv('LLMADDRESS')
llmPrivateKey = os.getenv('LLMPRIVATEKEY')



# Details of judge's address and private key stored in .env file
adminAddress = os.getenv('ADMINADRESS')
adminPrivateKey = os.getenv('ADMINPRIVATEKEY')

unitGasPrice = web3.eth.gas_price # to get the current gas price in wei
numberofTokens = 0 # the number of token that LLM returns is initialised to 0


# Function definition to send a prompt to LLaMA2 and receive a response
def sendPrompt(prompt,responseLimit, max_tokens=1, temperature=0.7):
    max_tokens = int(responseLimit)
    Max_tokensAllowed = 300
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
        #print("number of tokesns",result["usage"]["completion_tokens"])# printed to test
        return result["choices"][0]["message"]["content"],numberofTokens
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None

# Function to listen for events from smart contract and update responses
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
            #print ("queryfee in ether is :",queryfeeinEther )
            print(f"Processing query {queryId} for user {userAddress}: {submittedQuery}")
            feesPaid = event['args']['fee']
            #print(f"fees paid is :{Web3.from_wei(feesPaid, 'ether')} Ether")
            responseCharLimit = (feesPaid - queryfeeinEther )/unitFee
            #print ("responseCharLimit is :",int(responseCharLimit)) #printed to test

            
            # Process the query using LLAMA2
            response,numberofTokens = sendPrompt(submittedQuery,responseCharLimit-1)
            if response:
                nonce = web3.eth.get_transaction_count(llmAddress)
                responseFee = numberofTokens * unitFee
                print("response is ",response) #printed to test 
                
                #print ("resposne fee before sending ",responseFee) # printed to test
                #response = 'a'# to test the cost
                gasEstimate = contract.functions.updateResponse(userAddress, queryId, response,queryFee,responseFee).estimate_gas({'from': llmAddress})
                transaction = contract.functions.updateResponse(userAddress, queryId, response,queryFee,responseFee).build_transaction({
                    'from': llmAddress,
                    'nonce': nonce,
                    #'gas': 1500000, # later estimate the price and used
                    'gas' :gasEstimate,
                    'gasPrice': unitGasPrice,
                })
                signedTransaction = web3.eth.account.sign_transaction(transaction, llmPrivateKey)
                transactionHash = web3.eth.send_raw_transaction(signedTransaction.rawTransaction)
                transactionReceipt = web3.eth.wait_for_transaction_receipt(transactionHash)
                print(f"Response for query {queryId} updated on blockchain for user {userAddress}.")
                print(f"Transaction hash for updating response is : {web3.to_hex(transactionHash)}")
                print("Updated the response on blockchain")
                #gasUsed = transactionReceipt.gasUsed # printed to know the gas used
                gasPriceinWei = web3.eth.get_transaction(transactionHash).gasPrice
                totalgasPrice = gasPriceinWei * transactionReceipt.gasUsed
                #print ("gas price in wei",gasPriceinWei)  # printed to know the gs price in wei
                print ("gas used ",transactionReceipt.gasUsed)
                print("Gas Price for updating gresponse is : ",totalgasPrice)
                print("Gas Price in ether updating gresponse is: ",web3.from_wei(totalgasPrice, 'ether'),"Ether")
                print("Gas Price in USD updating gresponse  is: ",web3.from_wei(totalgasPrice, 'ether')*2610)   # to estimate the price in usd -this was to test            

                #printing the llm fee which is the total amount of query processing and response retriving
                for event in eventfilterResponseFee.get_new_entries():
                    totaLlmFee = event['args']['totaLlmFee']
                    print("Response fee in wei is ",totaLlmFee) # to know the LLM fee printed this 
                    print("Response fee in ether is :",Web3.from_wei(totaLlmFee, 'ether'),"Ether")
                    

                # printing the refund amount which will be refunded to user's account which is balance amount after processing the wuery and updating the response
                for event in eventfilterRefund.get_new_entries():
                    refund = event['args']['refund']
                    #print("Refund amount in wei is ",refund)
                    print(f"Refund fee in ether is :{Web3.from_wei(refund, 'ether')} Ether")
                 
                   
                
            else:
                print(f"Failed to generate response for query {queryId}")

        await asyncio.sleep(5)

# this event is from smart contract to verify the response already stored  to decide whether to process compensation or not 
#verification was done using Mystral 7b

async def eventListenerCompensation():
    eventfilterCompensation = contract.events.requestCompensation.create_filter(fromBlock='latest')
    while True:
        for event in eventfilterCompensation.get_new_entries():
            userAddress = event['args']['user']
            queryId = event['args']['queryID']
            givenQuery = event['args']['givenQuery']
            givenResponse = event['args']['givenResponse']
            #givenResponse = "vnmvn" # used for testing purpose
            print ("Given Response",givenResponse) # this was th eresposne already stored on blockchina
            print(f"Processing compensation request for user {userAddress}: queryId {queryId}")

            #newQuery = "answer to the question  "+givenQuery+"+is "+givenResponse+", is this is correct give only true or false answer no description please"
       
            newQuery = "answer to the question which is the capital of japan is america , is this correct give true or false answer , no description please" 
            # the above line of code was written to checke whether compensation mechanism is working when the reposne is wrong
            # Process the query using LLaMA2 and verify
            responseLimit =100 # set the max_tocken to 300  to because the original tocken size was also 300 and later changed to 100 since we only need a true or false value
            #verifiedResponse ,numberofTokens= sendPrompt(givenQuery,responseLimit) 
            verifiedResponse ,numberofTokens= sendPrompt(newQuery,responseLimit)

            if verifiedResponse: 
                print(f"checked query and new Generated response is:{verifiedResponse}")
                verifiedResponse.replace(" ","")
                print(len(verifiedResponse))
   
                verifiedResponse = verifiedResponse[1:5]
                print("verified resonse is",verifiedResponse)
                #if verifiedResponse != givenResponse:
                if verifiedResponse !="True":
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
                    #gasUsed = transactionReceipt.gasUsed # this is printed to know the gas used for transaction
                    gasPriceinWei = web3.eth.get_transaction(transactionHash).gasPrice
                    print ("gas price in wei",gasPriceinWei)
                    print ("gas used ",transactionReceipt.gasUsed)
                    # gas price in ether = gas price in gwei * gas used * conversion factor
                    totalgasPrice = gasPriceinWei * transactionReceipt.gasUsed
                    print("Gas Price in gwei for updating for  compensation is : ",totalgasPrice)
                    print("Gas Price in ether for  updating compensation is: ",web3.from_wei(totalgasPrice, 'ether'),"Ether")
                    print("Gas Price in USD for updating compensation  is: ",web3.from_wei(totalgasPrice, 'ether')*2610) #printed this for testing purpose on the basis 1ETH = 2610 USD
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





    
