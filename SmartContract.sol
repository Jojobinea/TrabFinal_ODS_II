// SPDX-License-Identifier: MIT

//["Qual é a capital da França?", "Quantos planetas existem no Sistema Solar?", "Quem desenvolveu a Teoria da Relatividade?", "Que cor resulta da mistura de azul com amarelo?", "Quanto é 9 x 7?"], ["Paris", "8", "Einstein", "Verde", "63"]

pragma solidity ^0.8.0;

contract EduQuiz {
    address public owner;
    string[] public questions;
    bytes32[] private answersHash;

    event AnswerAttempt(address indexed player, string answer, bool correct);
    event RewardSent(address indexed to, uint256 amount);

    constructor(string[] memory _questions, string[] memory _answers) payable {
        require(_questions.length == _answers.length, "Perguntas e respostas nao coincidem.");
        owner = msg.sender;

        for (uint256 i = 0; i < _questions.length; i++) {
            questions.push(_questions[i]);
            answersHash.push(keccak256(abi.encodePacked(_answers[i])));
        }
    }

    function getQuestions() public view returns (string[] memory) {
        return questions;
    }

    function answerBatch(string[] memory answers) public {
        require(answers.length == questions.length, "Numero incorreto de respostas.");

        uint256 correctCount = 0;

        for (uint256 i = 0; i < answers.length; i++) {
            bool correct = keccak256(abi.encodePacked(answers[i])) == answersHash[i];
            emit AnswerAttempt(msg.sender, answers[i], correct);
            if (correct) {
                correctCount++;
            }
        }

        uint256 reward = correctCount * 0.001 ether;
        require(address(this).balance >= reward, "Contrato sem saldo suficiente.");

        if (reward > 0) {
            payable(msg.sender).transfer(reward);
            emit RewardSent(msg.sender, reward);
        }
    }

    function checkAnswers(string[] memory answers) public view returns (bool[] memory) {
        require(answers.length == questions.length, "Numero incorreto de respostas.");
        bool[] memory result = new bool[](answers.length);

        for (uint256 i = 0; i < answers.length; i++) {
            result[i] = (keccak256(abi.encodePacked(answers[i])) == answersHash[i]);
        }

        return result;
    }

    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }

    receive() external payable {}
}
