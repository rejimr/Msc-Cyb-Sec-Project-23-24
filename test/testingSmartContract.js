const AIInsurance = artifacts.require("SmartContractAICompensation"); // Import the smart contract and stor int in a vairable AIinsurance

contract("AIInsurance", (accounts) => {
  let AIInsuranceContract;

  // Ensure smart contract is deployed before all tests 
  before(async () => {
    AIInsuranceContract = await AIInsurance.deployed(); // AIInsurance.deployed() get the instanc of the contract and store in AIInsuranceContract 

  });
    // test case for addQuery()
  
  it("checking function to submit a query", async () => {
    let queryFee = web3.utils.toWei('0.005', 'ether'); // query fee
    await AIInsuranceContract.addQuery("What is AIQuery to LLLM?", queryFee, { from: accounts[0], value: web3.utils.toWei('0.5', 'ether') }); // account [0] is user accout 
  });

    // test case for updateResponse()

  it("checking function to update the response", async () => {
    await AIInsuranceContract.updateResponse(accounts[0], 1, "Answer from LLM", 1000, 1000, { from: accounts[1] }); // account [1] is accout of LLM
  });

 // test case for checkingQuerycompn()

  it("checking the  compensation request", async () => {
    await AIInsuranceContract.checkingQuerycompn(accounts[0], 1, { from: accounts[0] });
  });


  // test case for compensationPayment()


  it("checking compensation payment", async () => {
    await AIInsuranceContract.compensationPayment(accounts[0], 1, { from: accounts[2] }); // account [2] is accout of judge
  });
});