---
layout: post
title: A Tact primer for Solidity developers - part 1 
tags: [tutorial, tact, solidity, ton, blockchain]
---

## Introduction

Solidity veterans, ever considered taking a walk on the wild side with TON and its smart contract language, Tact? This tutorial will be your trusty compass. While both Solidity and Tact empower you to build smart contracts, the underlying blockchains, particularly in terms of state management and asynchronous calls, have some key distinctions. Grasping these differences is essential for a smooth trip.

Let's start with a superficial look into syntax and structure.

## A simple counter contract

Let's look at this Simple Counter contract form [Tact by Example](https://tact-by-example.org/01-a-simple-counter):

```tact
contract Counter {
 
    // persistent state variable of type Int to hold the counter value
    val: Int as uint32;
 
    // initialize the state variable when contract is deployed
    init() {
        self.val = 0;
    }
 
    // handler for incoming increment messages that change the state
    receive("increment") {
        self.val = self.val + 1;
    }
 
    // read-only getter for querying the counter value
    get fun value(): Int {
        return self.val;
    }
}
```

and for Solidity:

```solidity
pragma solidity ^0.8.4;

contract Counter {
    int private count = 0;

    function increment() public {
        count += 1;
    }

    function value() public view returns (int) {
        return count;
    }
}
```

At first glance, both contracts share a similar structure: they define a contract name, state variables, and functions. I won't get into superficial details like the difference in keywords. The important thing to pay attention here is that Tact employs message handlers (receive) for incoming messages, while Solidity relies on traditional function calls (increment). This is the key to understanding the difference between Solidity and Tact.

## Message passing

All interaction between contracts in TON works through messages. This means the state of a contract is a function of its initial state and the messages it received, almost as a small blockchain by itself. A TON contract state does not depend on the state of another contract. This messaging approach enables scalability, but it can make code slightly more complex to write compared to Solidity's function calls.

## Getters

You may notice there's a `get` kwyword in the Tact example above. Getters are meant for programatic interaction with DApps or wallets and can't be called by other contracts.

## For future

The next installment of this series will be a comparison between ERC-20 tokens and Jettons, TON's native token standard.
