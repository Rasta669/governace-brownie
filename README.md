# governace-brownie
this is a simple implementation of smart contract governance, with erc20 governance token.

# @dev
the timelock is the admin of our governance.

account is the admin of the timelock, in real-life application gnosis safe multisig usually is the owner of the timelock.

to transfer ownesrship; revokeRole() of previous owner(acc), then grantRole() to new owner.

these contracts are both tested on local blockchain(ganache) and on goerli testnet.
