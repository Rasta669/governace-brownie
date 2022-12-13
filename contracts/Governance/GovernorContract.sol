// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/governance/Governor.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorSettings.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorCountingSimple.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorVotes.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorVotesQuorumFraction.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorTimelockControl.sol";

/*
Voting Delay = 1 - 1 block = 12 seconds
voting period = 50400 = 1 week
*/
contract GovernorContract is
    Governor,
    GovernorCountingSimple,
    GovernorVotes,
    GovernorVotesQuorumFraction,
    GovernorTimelockControl
{
    uint256 s_votingPeriod;
    uint256 s_votingDelay;

    constructor(
        IVotes _token,
        TimelockController _timelock,
        string memory governorName,
        uint256 voting_delay,
        uint256 voting_period,
        uint256 quorumPercentage
    )
        Governor(governorName)
        GovernorVotes(_token)
        GovernorVotesQuorumFraction(quorumPercentage)
        GovernorTimelockControl(_timelock)
    {
        s_votingDelay = voting_delay;
        s_votingPeriod = voting_period;
    }

    // constructor(
    //     IVotes _token,
    //     TimelockController _timelock,
    //     string memory governorName,
    //     uint256 voting_delay,
    //     uint256 voting_period,
    //     uint256 quorumPercentage
    // )
    //     Governor(governorName)
    //     GovernorSettings(voting_delay, voting_period, 1e18)
    //     GovernorVotes(_token)
    //     GovernorVotesQuorumFraction(quorumPercentage)
    //     GovernorTimelockControl(_timelock)
    // {}

    // The following functions are overrides required by Solidity.

    function votingDelay() public view override returns (uint256) {
        return s_votingDelay; // 1 = 1 block
    }

    function votingPeriod() public view override returns (uint256) {
        return s_votingPeriod; // 45818 = 1 week
    }

    function quorum(uint256 blockNumber)
        public
        view
        override(IGovernor, GovernorVotesQuorumFraction)
        returns (uint256)
    {
        return super.quorum(blockNumber);
    }

    function state(uint256 proposalId)
        public
        view
        override(Governor, GovernorTimelockControl)
        returns (ProposalState)
    {
        return super.state(proposalId);
    }

    function propose(
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        string memory description
    ) public override(Governor, IGovernor) returns (uint256) {
        return super.propose(targets, values, calldatas, description);
    }

    function proposalThreshold()
        public
        view
        override(Governor)
        returns (uint256)
    {
        return super.proposalThreshold();
    }

    function _execute(
        uint256 proposalId,
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        bytes32 descriptionHash
    ) internal override(Governor, GovernorTimelockControl) {
        super._execute(proposalId, targets, values, calldatas, descriptionHash);
    }

    function _cancel(
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        bytes32 descriptionHash
    ) internal override(Governor, GovernorTimelockControl) returns (uint256) {
        return super._cancel(targets, values, calldatas, descriptionHash);
    }

    function _executor()
        internal
        view
        override(Governor, GovernorTimelockControl)
        returns (address)
    {
        return super._executor();
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(Governor, GovernorTimelockControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
