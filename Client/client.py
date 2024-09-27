import json
from web3 import Web3
import time
import traceback
from dotenv import load_dotenv
import os
load_dotenv()

#use smart contract address and abi and the url denotes the url of Ganache
url = "HTTP://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(url))
#abi = json.loads('[ { "inputs": [ { "internalType": "address payable", "name": "_llmAddress", "type": "address" }, { "internalType": "address", "name": "_adminAddress", "type": "address" } ], "stateMutability": "payable", "type": "constructor", "payable": true }, { "anonymous": false, "inputs": [ { "indexed": false, "internalType": "uint256", "name": "refund", "type": "uint256" } ], "name": "printRefund", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": false, "internalType": "uint256", "name": "totaLlmFee", "type": "uint256" } ], "name": "printResponseFee", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "user", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "queryID", "type": "uint256" }, { "indexed": false, "internalType": "string", "name": "givenQuery", "type": "string" }, { "indexed": false, "internalType": "string", "name": "givenResponse", "type": "string" } ], "name": "requestCompensation", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "user", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "queryID", "type": "uint256" }, { "indexed": false, "internalType": "string", "name": "query", "type": "string" }, { "indexed": false, "internalType": "uint256", "name": "fee", "type": "uint256" }, { "indexed": false, "internalType": "uint256", "name": "premium", "type": "uint256" } ], "name": "submittedQuery", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "user", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "queryID", "type": "uint256" }, { "indexed": false, "internalType": "bool", "name": "isPaid", "type": "bool" } ], "name": "triggeringCompensation", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "user", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "queryID", "type": "uint256" }, { "indexed": false, "internalType": "string", "name": "response", "type": "string" } ], "name": "updatedResponse", "type": "event" }, { "inputs": [], "name": "adminAddress", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "stateMutability": "view", "type": "function", "constant": true }, { "inputs": [], "name": "llmAddress", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "stateMutability": "view", "type": "function", "constant": true }, { "inputs": [ { "internalType": "address", "name": "", "type": "address" }, { "internalType": "uint256", "name": "", "type": "uint256" } ], "name": "llmQueryResponse", "outputs": [ { "internalType": "address", "name": "user", "type": "address" }, { "internalType": "string", "name": "query", "type": "string" }, { "internalType": "string", "name": "response", "type": "string" }, { "internalType": "uint256", "name": "fee", "type": "uint256" }, { "internalType": "uint256", "name": "premium", "type": "uint256" }, { "internalType": "bool", "name": "paidCompensation", "type": "bool" } ], "stateMutability": "view", "type": "function", "constant": true }, { "inputs": [ { "internalType": "address", "name": "", "type": "address" } ], "name": "queryCount", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "stateMutability": "view", "type": "function", "constant": true }, { "inputs": [], "name": "unitFee", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "stateMutability": "view", "type": "function", "constant": true }, { "inputs": [ { "internalType": "address", "name": "", "type": "address" }, { "internalType": "uint256", "name": "", "type": "uint256" } ], "name": "userQueryDetails", "outputs": [ { "internalType": "address", "name": "user", "type": "address" }, { "internalType": "string", "name": "query", "type": "string" }, { "internalType": "string", "name": "response", "type": "string" }, { "internalType": "uint256", "name": "fee", "type": "uint256" }, { "internalType": "uint256", "name": "premium", "type": "uint256" }, { "internalType": "bool", "name": "paidCompensation", "type": "bool" } ], "stateMutability": "view", "type": "function", "constant": true }, { "inputs": [ { "internalType": "string", "name": "_query", "type": "string" }, { "internalType": "uint256", "name": "_queryFee", "type": "uint256" } ], "name": "addQuery", "outputs": [], "stateMutability": "payable", "type": "function", "payable": true }, { "inputs": [ { "internalType": "address", "name": "_user", "type": "address" }, { "internalType": "uint256", "name": "_queryId", "type": "uint256" }, { "internalType": "string", "name": "_response", "type": "string" }, { "internalType": "uint256", "name": "_queryfee", "type": "uint256" } ], "name": "updateResponse", "outputs": [], "stateMutability": "payable", "type": "function", "payable": true }, { "inputs": [ { "internalType": "address", "name": "_address", "type": "address" }, { "internalType": "uint256", "name": "_id", "type": "uint256" } ], "name": "getQueryResponse", "outputs": [ { "components": [ { "internalType": "address", "name": "user", "type": "address" }, { "internalType": "string", "name": "query", "type": "string" }, { "internalType": "string", "name": "response", "type": "string" }, { "internalType": "uint256", "name": "fee", "type": "uint256" }, { "internalType": "uint256", "name": "premium", "type": "uint256" }, { "internalType": "bool", "name": "paidCompensation", "type": "bool" } ], "internalType": "struct SmartContractAICompensation.QueryDetails", "name": "", "type": "tuple" } ], "stateMutability": "view", "type": "function", "constant": true }, { "inputs": [ { "internalType": "address", "name": "_user", "type": "address" }, { "internalType": "uint256", "name": "_queryId", "type": "uint256" } ], "name": "checkingQuerycompn", "outputs": [], "stateMutability": "nonpayable", "type": "function" }, { "inputs": [ { "internalType": "address", "name": "_user", "type": "address" }, { "internalType": "uint256", "name": "_queryId", "type": "uint256" } ], "name": "compensationPayment", "outputs": [], "stateMutability": "payable", "type": "function", "payable": true } ]')
# Load the contract ABI from the compiled SmartContractAICompensation.json file (build file)
with open('build/contracts/SmartContractAICompensation.json') as contractj:
    jsonContract = json.load(contractj)
    abi = jsonContract['abi']

#current contract address , the your address is the af=ddress of the user and its corresponding privat key 

contractaddress = os.getenv('CONTRACTADRESS')
contract = web3.eth.contract(address=contractaddress, abi=abi)
userAddress=os.getenv('CLIENTADDRESS')
userPrivateKey=  os.getenv('CLIENTPRIVATEKEY')
unitGasPrice = web3.eth.gas_price


#fuction to add query to blockchain ,the function addquery from smartt contrat is called here
def submitQuery(query,userfee):
    queryLength = len(query)
    unitFee = web3.to_wei('0.0001','ether')# unit fee for query per character
    queryFee = queryLength * unitFee
    userPayment = web3.to_wei(userfee, 'ether')
    if userPayment < queryFee:
        print ("Fees paid is insufficient for processing your query")
        return
    nonce = web3.eth.get_transaction_count(userAddress)
    print ("unit gas price is ", unitGasPrice)
    transaction = contract.functions.addQuery(
        query,queryFee).build_transaction({
        'gas': 200000,
        'gasPrice': unitGasPrice,
        'from': userAddress,#use your address which uses AI
        'nonce': nonce,
        'value' : userPayment
        })

    #use private key of the user account , the corresponding trasaction hash and recipt for updating query on the blockchain
    signedTransaction = web3.eth.account.sign_transaction(transaction,userPrivateKey)
    transactionHash=web3.eth.send_raw_transaction(signedTransaction.rawTransaction)
    transactionReceipt = web3.eth.wait_for_transaction_receipt(transactionHash)
    print(f"Transaction hash: {web3.to_hex(transactionHash)}")
    print("Updated the query")
    gasPriceinWei = web3.eth.get_transaction(transactionHash).gasPrice
    totalgasPrice = gasPriceinWei * transactionReceipt.gasUsed
    print ("gas price in wei",gasPriceinWei)
    print ("gas used ",transactionReceipt.gasUsed)
    print("Gas Price for adding the query: ",totalgasPrice)
    print("Gas Price in ether for adding the query is :  ",web3.from_wei(totalgasPrice, 'ether'),"Ether")
    print("Gas Price in USD for adding the query  is: ",web3.from_wei(totalgasPrice, 'ether')*2500)
    

    queryCount=contract.functions.queryCount(userAddress).call() 
    responseReceived = False
    polling_interval = 5  # seconds

    while not  responseReceived:
        print("Checking for response...")
        queryDetails = getValue(userAddress, queryCount)
        response = queryDetails['response']
        
        if response:
            print("Response received:")
            print(f" query ID: {queryCount}")
            print(queryDetails)
            responseReceived = True
        else:
            print("No response yet. Retrying...")
            time.sleep(polling_interval)




# this function is to get the details of user , address, query, fee etc from blockchain has been fetched and displayed 
def getValue(addres,id):
    try:
        temp=contract.functions.getQueryResponse(addres,id).call()
        return{
        'user address':temp[0],
        'query' :temp[1],
        'response': temp[2],
        'fee': temp[3],
        'premium':temp[4],
        'paidCompensation': temp[5]           
  }
    except Exception as e:
        print ("Error :{(e)}")  
        return None

# function to request for compensation
def compensationRequest(address,id):
    try:
        print ("Checking the query id is valid or not")
        queryCount=contract.functions.queryCount(userAddress).call() # getting the last query if from blockchain
        print ("the last query id is :" ,queryCount)
        if id>queryCount or id <0 :
            print ("Invalid query id please give a valid query id")
            return
        print( "checking if already paid compensation")
        detailsComp = getValue(address,id)
        
        print(detailsComp['paidCompensation'])
        _isPaid = detailsComp['paidCompensation']
        

        

        if _isPaid:
            
            print("already paid compensation")
            return
            
        else:
            nonce = web3.eth.get_transaction_count(userAddress)
            trasactionComp = contract.functions.checkingQuerycompn(address,id).build_transaction({
                'gas': 200000,
                'gasPrice': unitGasPrice,
                'from': userAddress,#use your address which uses AI
                'nonce': nonce,
                'value': web3.to_wei('0', 'ether')  # Adjust the value if needed  
        
                })
            signedTransaction = web3.eth.account.sign_transaction(trasactionComp,userPrivateKey)
            transactionHash=web3.eth.send_raw_transaction(signedTransaction.rawTransaction)
            transactionReceipt = web3.eth.wait_for_transaction_receipt(transactionHash)
            print(f"Transaction hash for checking compensation: {web3.to_hex(transactionHash)}")
            #gasUsed = transactionReceipt.gasUsed
            gasPriceinWei = web3.eth.get_transaction(transactionHash).gasPrice
            totalgasPrice = gasPriceinWei * transactionReceipt.gasUsed
            print ("gas price in wei",gasPriceinWei)
            print ("gas used ",transactionReceipt.gasUsed)
            print("Gas Price for  compensation request is : ",totalgasPrice)
            print("Gas Price in ether  compensation request  is: ",web3.from_wei(totalgasPrice, 'ether'),"Ether")
            print("Gas Price in USD  compensation  request is: ",web3.from_wei(totalgasPrice, 'ether')*2500)


            print(f" query ID for compensation is :  {id}")
            print ("Request for compensation has been submitted pleas wait for response...")
                     
            
            
            responseforCompesation = False
            polling_interval = 40


            while not  responseforCompesation:
                print("Checking for compensation request response...")
                time.sleep(polling_interval)
                updatedRequestDetails = getValue(userAddress, id)
                response = updatedRequestDetails['paidCompensation']
                
                if response == True:
                    print("compensation received:")
                    print("Paid Compensation True/False : ",updatedRequestDetails['paidCompensation'])
                    print(f"Compensation for query {id} processed for user {address}.")
                    print("Premium amount has been updated as ",updatedRequestDetails['premium'])
                    #print(updatedRequestDetails['paidCompensation'])
                    responseforCompesation = True
                elif response == False:
                    print("No compensation , it cannot be processed (response came to be right):")
                    print("Paid Compensation True/False : ",updatedRequestDetails['paidCompensation'])
                    print(f"Compensation for query {id} cannot be processed for user {address}.")
                    responseforCompesation = True
                else:
                    print("No compensation , it cannot be processed ..")
                    time.sleep(polling_interval)


            
    except Exception as e:
        #print ("Error :{e}")  
        #traceback.print_exc()
        print ("Please give a valid query id")
        return None

#main program
if __name__ == "__main__":
    while True:
        print ("\nEnter the choice from the below options , what you want to do? :")
        print ("option 1. Submit a query to LLM")
        print ("option 2. Claim Compensation")
        print ("option 3. Exit")
        option = input ("Enter your option here(1/2/3): ")

        if option =="1":
            query = input("Enter your query to LLM here: ")
            userPayment =float(input("Enter the fees you want to pay for usig LLM: "))
            submitQuery(query,userPayment)

        elif option == "2":
            queryId = int(input("Enter the query Id which you believe is wrong to make a claim: "))
            compensationRequest(userAddress, queryId)            

        elif option == "3":
            print("Exiting the program")
            break
        else:
            print("Invalid option, please try again.")



 