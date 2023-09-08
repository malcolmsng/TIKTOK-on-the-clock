// SPDX-License-Identifier: MIT
import "./StringUtils.sol";
pragma solidity ^0.8.19;

contract TTWallet {
    
    address public owner;
    string public id;
    string public hashedPin;
    
    constructor(
        string memory _id,  string memory _hashedPin
        ) {
        owner = msg.sender;
        id = _id;
        hashedPin = _hashedPin;

    }

    modifier onlyOwner {
        require(msg.sender == owner, "caller is not owner");
        _;
    }

    modifier correctId(string memory _id){
        require(Strings.equals(Strings.toSlice(id),Strings.toSlice(_id)), "Wrong ID");
        _;
    }

    modifier correctPin( string memory _hashedPin){
       require(Strings.equals(Strings.toSlice(hashedPin),Strings.toSlice(_hashedPin)), "Wrong ID");
        _;
    }

    modifier balanceAvaiailable(uint _amount) {
        require(_amount <= address(this).balance, "Not enough balance in wallet");
        _;
    }

    event Pay(uint _amount, string id, string _hashedPin, address _recipient);

    function pay(uint _amount, string calldata _id, string calldata _hashedPin, address _recipient) external onlyOwner correctId(_id) correctPin(_hashedPin) {
        payable(_recipient).transfer(_amount);
        emit Pay(_amount, id, _hashedPin, _recipient);
    }
    
    function getBalance() external view returns (uint) {
        return address(this).balance;
    }
    receive() external payable {
    }
    fallback() external payable {}
}