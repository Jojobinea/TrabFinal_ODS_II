// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EduQuiz {
    address public owner;
    string public question;
    bytes32 private answerHash;

    constructor(string memory _question, string memory _answer) payable {
        owner = msg.sender;
        question = _question;
        answerHash = keccak256(abi.encodePacked(_answer));
    }

    function getQuestion() public view returns (string memory) {
        return question;
    }

    function answer(string memory _answer) public {
        require(address(this).balance >= 0.001 ether, "Not enough reward");
        require(keccak256(abi.encodePacked(_answer)) == answerHash, "Wrong answer");
        payable(msg.sender).transfer(0.0001 ether);
    }

    receive() external payable {} // Permite receber ETH
}
