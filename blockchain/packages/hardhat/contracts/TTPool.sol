// SPDX-License-Identifier: MIT
import "./TTT.sol";
pragma solidity ^0.8.9;

// buyers pay to TTWalletManager
contract TTWalletManager {
	address owner;
	IERC20 private TTT;
	mapping(string => uint) idToBalance;
	mapping(string => address) idToAddress;

	constructor(IERC20 token) {
		owner = msg.sender;
		TTT = token;
	}

	event Registered(string tiktokId, address userAddress);
	event Paid(string sender, string recipient, uint amt);

	// event BuyerDeposited(string sellerTiktokId, string buyerTiktokId);

	function register(string memory tiktokId, address userAddress) external {
		require(msg.sender == owner);
		idToAddress[tiktokId] = userAddress;
		idToBalance[tiktokId] = 0;
		emit Registered(tiktokId, userAddress);
	}

	function pay(
		string memory sender,
		string memory recipient,
		uint amt
	) external payable {
		uint senderBal = idToBalance[sender];
		require(idToAddress[sender] != address(0));
		require(idToAddress[recipient] != address(0));
		require(senderBal >= amt, "Sender needs more TTT");
		address senderAdd = idToAddress[sender];
		address recipientAdd = idToAddress[recipient];
		idToBalance[sender] -= amt;
		idToBalance[recipient] += amt;
		TTT.transferFrom(senderAdd, recipientAdd, amt);
		emit Paid(sender, recipient, amt);
	}

	function getBalance() external view returns (uint) {
		return address(this).balance;
	}

    function withdraw() external {
        
    }

	// function getSellers() external view returns (TTWallet[] memory) {
	// 	return sellers;
	// }

	function getUserBalance(string memory ttId) external view returns (uint) {
		return idToBalance[ttId];
	}
}
