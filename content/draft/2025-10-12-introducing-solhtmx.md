---
date: "2025-10-12T00:00:00Z"
tags:
    - solana
    - htmx 
    - blockchain
    - web3
title: "solhtmx: Simpler Solana Interactions with HTML Attributes"
---

## Introduction

solhtmx is a Solana-native extension to htmx that simplifies blockchain interactions using HTML attributes. It lets you:

- Connect wallets
- Sign transactions 
- Interact with Solana 

All using declarative HTML, without complex JavaScript.

## Problem

Building blockchain apps typically involves:

1. Complex wallet SDKs
2. Managing connection state 
3. Handling transaction signing
4. Coordinating UI updates

This means lots of JavaScript and careful orchestration of async operations.

## Solution

solhtmx extends htmx with Solana-specific attributes:

- `sol-connect` - Connect wallet
- `sol-sign` - Sign transactions
- `sol-wallet-address` - Show wallet address 
- `sol-trigger` - React to blockchain events

### Connecting a Wallet

```html
<button sol-connect="true" 
        hx-get="/api/wallet-status"
        hx-target="#wallet-info">
  Connect Wallet
</button>
```

Clicking the button:
1. Prompts wallet connection
2. Triggers `/api/wallet-status` 
3. Includes wallet address in headers
4. Updates `#wallet-info` with response

### Signing Transactions

```html
<button sol-sign="true"
        hx-post="/api/prepare-transfer"
        hx-vals='{"amount": "0.1"}'
        hx-target="#result">
  Send 0.1 SOL
</button>
```

1. htmx POSTs to `/api/prepare-transfer`
2. Server builds unsigned transaction
3. Server returns HTML + transaction 
4. solhtmx prompts wallet signature
5. Submits signed transaction
6. Updates `#result` on confirmation

The server just builds transactions and returns HTML. solhtmx does the rest.

## Features

- Wallet connection
- Transaction signing
- Wallet address display
- Event system for updates
- Automatic header injection

## Usage

```html
<script src="https://unpkg.com/htmx.org@2.0.0"></script>
<script src="https://unpkg.com/@solana/web3.js@latest"></script>
<script src="path/to/solhtmx.js"></script>
```

Configure network via meta tags:

```html
<meta name="sol-network" content="devnet">
<meta name="sol-commitment" content="confirmed">
```

## Repo & Docs

Code, examples, docs:
**[github.com/vitorpy/solhtmx](https://github.com/vitorpy/solhtmx)**

Open source (WTFPL). Contributions welcome.

## Conclusion 

solhtmx simplifies Solana app development using declarative HTML attributes. Give it a try and share your feedback.
