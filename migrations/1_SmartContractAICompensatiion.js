var SmartContractAICompensation = artifacts.require("./SmartContractAICompensation.sol");

module.exports = async function(deployer, network, accounts) {
  //console.log("Accounts available:", accounts);

  
  const llmAddress = accounts[1]; 
  const adminAddress = accounts[2]; 

  console.log("Deploying with LLM Address:", llmAddress);
  console.log("Deploying with Admin Address:", adminAddress);

  await deployer.deploy(SmartContractAICompensation, llmAddress, adminAddress, {
    from: accounts[0],  // Deploy from the first account
    value: web3.utils.toWei('0', 'ether'),  // Initial ether if needed
    gas: 6000000  // Set an appropriate gas limit
  });
};
