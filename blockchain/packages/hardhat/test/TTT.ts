import { expect } from "chai";
import { ethers } from "hardhat";
import { TiktokToken } from "../typechain-types";
// import { YourContract } from "../typechain-types";

describe("TiktokToken", function () {
  let ttToken: TiktokToken;
  //   let tiktokToken;
  let owner: any;
  let addr1: any;

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();

    const TTTFactory = await ethers.getContractFactory("TiktokToken");
    ttToken = (await TTTFactory.deploy()) as TiktokToken;
    await ttToken.deployed();
  });

  it("Should deploy TiktokToken contract", async function () {
    expect(ttToken.address).to.not.equal(0);
  });
  it("Should have an initial supply of 1,000,000 tokens", async () => {
    const initialSupply = ethers.utils.parseUnits("1000000", 18); // Assuming 18 decimals
    expect(await ttToken.totalSupply()).to.equal(initialSupply);
  });

  it("Should have the correct name and symbol", async function () {
    expect(await ttToken.name()).to.equal("TiktokToken");
    expect(await ttToken.symbol()).to.equal("TTT");
  });

  it("Should allow minting by the owner", async function () {
    const initialBalance = await ttToken.balanceOf(addr1.address);
    const amountToMint = ethers.utils.parseEther("1000");

    await ttToken.connect(owner).mint(addr1.address, amountToMint);

    const finalBalance = await ttToken.balanceOf(addr1.address);

    expect(finalBalance.sub(initialBalance)).to.equal(amountToMint);
  });

  // Add more test cases as needed

  // You can also test functions like pause, unpause, and transfers.
});
