//SPDX Licence Identifier: MIT

/* This is the simple store and retrieve value contract 
with the main aim of demonstrating the use of transparent 
upgradeable proxy.
** The initializer fx aim is to replace the constructor as 
the use of proxy comes with constructor limitation
*/

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";

contract Box is Ownable {
    uint256 number;
    bool initialized;
    event numberChanged(uint256 newNumber);

    function initializer(uint256 nombre) public {
        require(!initialized);
        initialized = true;
        number = nombre;
    }

    function setNumber(uint256 newNumber) public onlyOwner {
        number = newNumber;
        emit numberChanged(newNumber);
    }

    function retrieve() public view returns (uint256) {
        return number;
    }
}
