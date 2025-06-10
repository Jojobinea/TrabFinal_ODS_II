// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EduQuiz {
    address public owner;
    string public question;
    bytes32 private answerHash;

    event AnswerAttempt(address indexed player, string answer, bool correct);
    event RewardSent(address indexed to, uint256 amount);

    constructor(string memory _question, string memory _answer) payable {
        owner = msg.sender;
        question = _question;
        answerHash = keccak256(abi.encodePacked(_answer));
    }

    function getQuestion() public view returns (string memory) {
        return question;
    }

    function answer(string memory _answer) public {
        bool correct = keccak256(abi.encodePacked(_answer)) == answerHash;
        emit AnswerAttempt(msg.sender, _answer, correct);

        require(correct, "Wrong answer");
        require(address(this).balance >= 0.0003 ether, "Not enough reward");

        // Pagar o jogador que respondeu corretamente
        payable(msg.sender).transfer(0.0003 ether);
        emit RewardSent(msg.sender, 0.0003 ether);
    }

    // Permite que qualquer pessoa envie ETH ao contrato
    receive() external payable {}

    // Verifica resposta sem executar pagamento
    function checkAnswer(string memory _answer) public view returns (bool) {
        return keccak256(abi.encodePacked(_answer)) == answerHash;
    }

    // Ver saldo do contrato (em Wei)
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}
