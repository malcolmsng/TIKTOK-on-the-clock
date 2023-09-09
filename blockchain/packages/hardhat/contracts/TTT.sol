// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract TiktokToken is ERC20, ERC20Burnable, Ownable {
	uint256 public rate; // Number of tokens per ETH. For example, if 1 ETH = 100 tokens, then rate = 100.

	mapping(string => uint) userBalance;
	// mapping(string => address) idToAddress;

	event Registered(string tiktokId);

	// function to check if address is contract
	function isContract(address _addr) public view returns (bool result) {
		uint32 size;
		assembly {
			size := extcodesize(_addr)
		}
		return (size > 0);
	}

	function checkAddress(address _address) internal view returns (bool) {
		return _address.balance > 0;
	}

	constructor(uint256 _rate) ERC20("TiktokToken", "TTT") {
		rate = _rate;
	}

	function setRate(uint256 _rate) external onlyOwner {
		rate = _rate;
	}

	function mint(address to, uint256 amount) internal {
		_mint(to, amount);
	}

	function deposit() public payable {
		require(msg.value > 0, "Must send ETH");

		// calculating the amount of TTT to transfer msg.sender
		uint256 tokensToMint = msg.value * rate;
		// transferring the said TTT to msg.sender
		mint(msg.sender, tokensToMint);
		// updating the userBalance
		// userBalance[tiktokusername] = userBalance[tiktokusername] + tokensToMint;
	}

	function withdraw(uint256 tttAmount) public {
		uint256 ethToTransfer = tttAmount / rate;

		require(
			address(this).balance >= ethToTransfer,
			"Not enough ETH in the contract"
		);
		require(
			balanceOf(msg.sender) >= tttAmount,
			"Not enough TTT tokens to withdraw"
		);

		// userBalance[tiktokusername] -= tttAmount;
		_burn(msg.sender, tttAmount);

		payable(msg.sender).transfer(ethToTransfer);
	}

	function redeemTokens(string memory username) public {
		// possibly can incorporate password verification next time to prevent ppl from stealing other ppls coins
		require(userBalance[username] > 0, "TikToker has no tokens to redeem");
		_transfer(address(this), msg.sender, userBalance[username]);
		userBalance[username] = 0;
	}

	function register(string memory tiktokId) external {
		userBalance[tiktokId] = 0;
		emit Registered(tiktokId);
	}

	function transferByUsername(string memory username, uint256 amount) public {
		require(
			balanceOf(msg.sender) >= amount,
			"Sender does not have enough TTT to send"
		);
		_transfer(msg.sender, address(this), amount);
		// update userBalances
		userBalance[username] = userBalance[username] + amount;
	}

	function transferByAddress(address to, uint256 amount) public {
		require(checkAddress(to), "Invalid recepient address");
		_transfer(msg.sender, to, amount);
	}

	function getTiktokBalance(
		string memory tiktokusername
	) external view returns (uint) {
		return userBalance[tiktokusername];
	}

	function _beforeTokenTransfer(
		address from,
		address to,
		uint256 amount
	) internal override {
		super._beforeTokenTransfer(from, to, amount);

		// ensure that the to address cannot equal to the address of the current contract
		// require(
		// 	to != address(this),
		// 	"Cannot transfer tokens to the contract itself"
		// );

		// require(
		// 	!isContract(to),
		// 	"Cannot transfer tokens to another contract address"
		// );
	}
}
