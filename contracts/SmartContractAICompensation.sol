// SPDX-License-Identifier: MIT
pragma solidity  0.8.1;
pragma experimental ABIEncoderV2;
contract SmartContractAICompensation
{    
    mapping (address=>uint) public queryCount;
    address public llmAddress;
    address public adminAddress;
    uint public unitFee = .001 ether;

    // variable to store the query details , the address of user, actual query, resposne the fee for LLM
    // , premium fee and the status of compensation whether paid or not
    struct QueryDetails
    {
        address user;
        string query;
        string response;
        uint fee;
        uint premium;
        bool paidCompensation;
    }
// creating object for QueryDetails , one for storing on user side and one on LLM side
    mapping ( address => mapping(uint => QueryDetails)) public userQueryDetails;
    mapping ( address => mapping(uint => QueryDetails)) public llmQueryResponse;

// events are emitted when there is an update on blockchain which listens by the server application
    event submittedQuery(address indexed user,uint queryID, string query, uint fee, uint premium);
    event updatedResponse(address indexed user,uint queryID, string response);
    event requestCompensation(address indexed user, uint queryID,string givenQuery,string givenResponse);
    event triggeringCompensation(address indexed user,uint queryID,bool isPaid);

// these two events are to for checkig the value to ensure the correct excecution of the program
    event printResponseFee(uint totaLlmFee);
    event printRefund(uint refund);

    constructor(address payable _llmAddress, address _adminAddress) payable {
        require(_llmAddress != address(0), "wrong LLM address.");
        require(_adminAddress != address(0), "wrong admin address.");
        llmAddress = _llmAddress;
        adminAddress = _adminAddress;
    }


    //Adding query and making a payment
    function addQuery(string memory _query,uint _queryFee) public payable{
       
        require(msg.value > _queryFee, "Ether is insufficient for processing the query");
        uint queryID=queryCount[msg.sender]+1;
        uint fee=msg.value/2;
        uint _premium = msg.value - fee;
        userQueryDetails[msg.sender][queryID]= QueryDetails(msg.sender,_query,'',fee,_premium,false);
        queryCount[msg.sender]=queryID;
        emit submittedQuery(msg.sender, queryID, _query, fee, _premium);
        }


    //Updating the query Response
    function updateResponse(address _user, uint _queryId,string memory _response,uint _queryfee,uint _responsefee) public payable{
        require(msg.sender == llmAddress , "only LLM can aupdate the response");
        uint responseFee = _responsefee;
        uint paidFees = userQueryDetails[_user][_queryId].fee;
        uint totaLlmFee = _queryfee + _responsefee;
        emit printResponseFee(totaLlmFee);
        require (paidFees >= responseFee,"Response is too big so insufficient LLM fee to process the request" );
        (bool success, ) = payable(llmAddress).call{value: totaLlmFee}("");
        require(success, "Transfer failed.");

        if (paidFees > responseFee){ 
            uint refund = paidFees-totaLlmFee;
            emit printRefund(refund);
            (bool refundSuccess,) = payable(_user).call{value: refund}("");
            require(refundSuccess, "Refund failed.");
        }

        // once the fees has been transferred to llm account the smartcontract variable of the user data has been updated with 0
        userQueryDetails[_user][_queryId].fee=0;
        userQueryDetails[_user][_queryId].response = _response;
        llmQueryResponse[llmAddress][_queryId]= QueryDetails(_user, userQueryDetails[_user][_queryId].query, _response, userQueryDetails[_user][_queryId].fee,userQueryDetails[_user][_queryId].premium, userQueryDetails[_user][_queryId].paidCompensation);
        llmQueryResponse[llmAddress][_queryId].fee = responseFee;
        emit updatedResponse(_user, _queryId, _response);
        }

    //function to get the details of user's query and response
    function getQueryResponse(address _address,uint _id) public view returns(QueryDetails memory)        {
            return userQueryDetails[_address][_id];
    }

     // function to get the details of the query that the user wants to challange and get compensation
    function checkingQuerycompn(address _user,uint _queryId) public  {
        require(_queryId <= queryCount[msg.sender], "Invalid query ID");
        require(msg.sender == userQueryDetails[_user][_queryId].user);
        string memory _givenResponse = userQueryDetails[_user][_queryId].response;
        string memory _givenQuery = userQueryDetails[_user][_queryId].query;        
        emit requestCompensation(_user,_queryId,_givenQuery,_givenResponse);
    }

     //Processing Compensation while AI repsone is wrong
    
    function compensationPayment(address _user,uint _queryId) public payable  {
        require(msg.sender == adminAddress , "only admins can initiate compensation");
        require(userQueryDetails[_user][_queryId].paidCompensation == false, "Already compensated");

        // uint compensationAmount = userQueryDetails[_user][_queryId].premium;
        require(_user.balance >= userQueryDetails[_user][_queryId].premium, "Insufficient contract balance");
        (bool success, ) = payable(_user).call{value: userQueryDetails[_user][_queryId].premium}(""); 
        require(success, "Transfer failed.");

        // the premium and paid compensation is updated once compensation has been paid to the user
        userQueryDetails[_user][_queryId].paidCompensation = true ;
        userQueryDetails[_user][_queryId].premium = 0;
        bool _isPaid = userQueryDetails[_user][_queryId].paidCompensation ;        
        emit triggeringCompensation(_user, _queryId,_isPaid);
    }
}












