// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EduQuiz {
    address public owner;
    string[] public questions;
    bytes32[] private answersHash;
    uint256 public rewardPerCorrect;
    uint256 public totalRewardSent;

    event AnswerAttempt(address indexed player, string answer, bool correct);
    event RewardSent(address indexed to, uint256 amount);

    constructor(
        string[] memory _questions,
        string[] memory _answers,
        uint256 _rewardPerCorrect
    ) payable {
        require(_questions.length == _answers.length, "Perguntas e respostas nao coincidem.");
        require(msg.value >= _rewardPerCorrect * _questions.length, "Valor inicial insuficiente para cobrir recompensas.");

        owner = msg.sender;
        rewardPerCorrect = _rewardPerCorrect;

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

        uint256 reward = correctCount * rewardPerCorrect;
        require(address(this).balance >= reward, "Contrato sem saldo suficiente.");

        if (reward > 0) {
            totalRewardSent += reward;
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
