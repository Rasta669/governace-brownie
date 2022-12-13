from scripts.helpful_scripts import get_account, LOCAL_DEVELOPMENT_NETWORKS
from brownie import (
    GovernanceToken,
    Box,
    GovernorContract,
    TimelockContract,
    network,
    Contract,
)
from web3 import Web3, constants
import time

min_delay = 1  # 1block- the timelock delay before the proposal is executed, check openzepplin-wizard for real coversion of real time eg 2days
voting_delay = 1  # 1 block- time delay from when the proposal was proposed to voting, also check openzepplin for actual conversion
voting_period = 5  # time open for voting
quorum_percentage = 4
description = "just store value"
## 0-against 1-for, 2 - abstain
# states{pending, active, cancelled, defeated, succeeded, queued, expired, executed}


def deploy_and_delegate():
    account = get_account()
    # deploying governance token
    gtoken = GovernanceToken.deploy("BujoToken", "BJT", {"from": account})
    print("Governance token deployed>>")
    # deploying timelock contract
    timelock = TimelockContract.deploy(
        min_delay, [], [], account, {"from": account}
    )  # an admin can be a multisig gnosis, for this project account is an admin
    print("timelock contract deployed!!")
    # deploying the governor contract.
    governor = GovernorContract.deploy(
        gtoken,
        timelock,
        "GovernorBujo",
        voting_delay,
        voting_period,
        quorum_percentage,
        {"from": account},
    )
    print("governor contract deployed<<")
    # assigning roles, by default the timelock admin is the contracts deployer
    proposers = timelock.PROPOSER_ROLE()
    executors = timelock.EXECUTOR_ROLE()
    # granting proposers role to the governor contract
    # timelock._setupRole(
    #     proposers, governor, {"from": account}
    # ) its an internal fx from accesscontrol.sol
    timelock.grantRole(proposers, governor, {"from": account})
    print("proposer role set")
    # granting excecutors role to every addresss
    timelock.grantRole(executors, constants.ADDRESS_ZERO, {"from": account})
    # timelock.grantRole(executors, governor, {"from": account})
    # timelock.grantRole(executors, account, {"from": account})
    print("executor role set")
    # delegating the vote.
    gtoken.delegate(account, {"from": account})
    return gtoken, timelock, governor, account


def deploy_box(account, timelock):
    account = account
    box = Box.deploy({"from": account})
    box.transferOwnership(timelock, {"from": account})
    return box


def propose(box, store_value, governor, account):
    args = (store_value,)
    calldata = box.setNumber.encode_input(*args)
    propose_tx = governor.propose(
        [box.address], [0], [calldata], description, {"from": account}
    )
    propose_tx.wait(3)  # to allow for voting delay period to pass
    proposalId = propose_tx.events["ProposalCreated"]["proposalId"]
    print(f"Proposal proposed, the state is {governor.state(proposalId)}")
    # moving voting_delay blocks to voting
    if network.show_active() in LOCAL_DEVELOPMENT_NETWORKS:
        move_blocks(voting_delay)
    print(proposalId)
    return propose_tx, proposalId, calldata


def vote(account, governor, proposalId: int, vote: int):
    if account:
        account = account
    else:
        account = get_account()
    if governor:
        governor = governor
    governor = GovernorContract[-1]
    vote_tx = governor.castVoteWithReason(
        proposalId, vote, "I love one", {"from": account}
    )
    vote_tx.wait(1 + voting_period)  # to allow for voting period to pass
    print(f"Yeay voted, the state is {governor.state(proposalId)}")
    if network.show_active() in LOCAL_DEVELOPMENT_NETWORKS:
        move_blocks(voting_period)
    # time.sleep(120)  # alternatively to allow voting period to pass
    print(f"Proposal voted for, the state is {governor.state(proposalId)}")


def queue(governor, box, calldata, account, proposalId):
    if account:
        account = account
    else:
        account = get_account()
    if governor:
        governor = governor
    governor = GovernorContract[-1]
    if box:
        box = box
    box = Box[-1]
    description_hash = Web3.keccak(text=description)  # .hex()
    queu_tx = governor.queue(
        [box.address], [0], [calldata], description_hash, {"from": account}
    )  # found in governortimelockcontrol.sol
    queu_tx.wait(1 + min_delay)  # to allow for min_delay period to pass
    print(f"Yeay the proposal is queued, the state is {governor.state(proposalId)}")
    # if network.show_active() in LOCAL_DEVELOPMENT_NETWORKS:
    #     move_blocks(min_delay)
    # time.sleep(60)  # alternatively this is to allow for min delay period to pass
    print(f"Proposal is queud, the state is {governor.state(proposalId)}")


def execute(governor, box, storeNum, account, proposalId):
    description_hash = Web3.keccak(text=description).hex()
    args = (storeNum,)
    encoded_fx = Contract.from_abi("Box", box.address, box.abi).setNumber.encode_input(
        *args
    )
    execute_tx = governor.execute(
        [box.address], [0], [encoded_fx], description_hash, {"from": account}
    )
    execute_tx.wait(1)
    print(f"the box value is now {box.retrieve()}")
    print(f"Yeay the proposal is executed, the state is {governor.state(proposalId)}")


def move_blocks(period):
    account = get_account()
    for block in range(period):
        tx = account.transfer(account, "0 ether")
        tx.wait(1)
    print(network.chain.height)
    print(f"Moved {period} blocks")


def main():
    gtoken, timelock, governor, account = deploy_and_delegate()
    box = deploy_box(account, timelock)
    # box = Box[-1]
    # governor = GovernorContract[-1]
    # account = get_account()
    propose_tx, propose_id, calldata = propose(box, 16, governor, account)
    # propose_id = (
    #     89348346465826725667282986671492679040912528930094721129822006870537472258777
    # )
    read_voting_block(propose_id)
    # args = (16,)
    # calldata = box.setNumber.encode_input(*args)
    vote(account, governor, proposalId=propose_id, vote=1)
    queue(governor, box, calldata=calldata, proposalId=propose_id, account=account)
    print(f"the state is {governor.state(propose_id)}")
    execute(governor, box, 16, account, propose_id)
    # move_blocks(5)


def read_voting_block(prop):
    governor = GovernorContract[-1]
    starting_voting_block = governor.proposalSnapshot(prop)
    voting_block = governor.proposalDeadline(prop)
    print(starting_voting_block)
    print(network.chain.height)
