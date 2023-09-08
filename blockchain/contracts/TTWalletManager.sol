// SPDX-License-Identifier: MIT
import "./StringUtils.sol";
pragma solidity ^0.8.19;

// buyers pay to TTWalletManager
contract TTWalletManager {
    address owner;
    mapping(address => uint) balances;
    // username to wallet address
    mapping(string => address) userToWallet;

    constructor() {
        owner = msg.sender;
    }

    event SellerRegistered(string tiktokId, address sellerAddress);
    event BuyerDeposited(string sellerTiktokId, string buyerTiktokId);

    function register(string memory tiktokId, address sellerAddress) external {
        require(msg.sender == owner);
        userToWallet[tiktokId] = sellerAddress;
        emit SellerRegistered(tiktokId, sellerAddress);
    }

    function buyerDeposit(
        string memory sellerTiktokId,
        string memory buyerTiktokId
    ) external payable {
        userToWallet[buyerTiktokId] = msg.sender;
        payable(userToWallet[sellerTiktokId]).transfer(msg.value);
        emit BuyerDeposited(sellerTiktokId, buyerTiktokId);
    }

    function getBalance() external view returns (uint) {
        return address(this).balance;
    }

    function getSellerBalance(
        string memory sellerTiktokId
    ) external view returns (uint) {
        return userToWallet[sellerTiktokId].balance;
    }
}
