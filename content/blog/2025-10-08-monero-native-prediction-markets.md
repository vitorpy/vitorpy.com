---
date: "2025-10-08T00:00:00Z"
tags: 
    - monero
    - defidate: "2021-11-30T00:00:00Z"
    - fhe
title: Monero Native Prediction Markets with FHE
latex: true
---

## Background

Talking to my friend Kyle Corsola at Token 2049, he suggested something fascinating: Monero native DeFi. Can we build something on the most OG of the privacy cryptocurrencies without compromising its privacy aspects?

Monero design makes creating native DeFi primitives really hard. I think it's possible to build Monero native prediction markets. There are probably other primitives to build with some creativity. To build this Goldberg machine, we take Monero, ring signatures and Zama's tfhe-rs.

## The Problem

Prediction markets need:
1. Collect bets on outcomes
2. Resolve with real-world result  
3. Calculate proportional payouts
4. Distribute winnings

Adding privacy constraints:
- Calculate payouts without knowing individual bets
- Prove winners without revealing bet details
- Prevent operator theft
- Use only Monero's existing primitives

Requirements:
- Compute on encrypted data for fair payouts
- No custom tokens or Monero modifications
- Trustless fund custody
- Practical performance with GPU acceleration

## Technical Approach

We use [Fully Homomorphic Encryption](https://en.wikipedia.org/wiki/Homomorphic_encryption) to compute on encrypted bets. Specifically, TFHE for exact integer arithmetic on financial amounts.

Components:
- **TFHE-rs**: Compute payouts on encrypted bets
- **Monero ring signatures**: Hide transaction graph
- **Stealth addresses**: One-time addresses for payouts
- **2-of-2 Multisig**: Coordinator + Oracle control funds
- **Commitment scheme**: Link bets to claims without revealing identity

## Monero Primitives

### Ring Signatures

Monero uses ring signatures to hide the true spender in a transaction. When spending, you create a ring of possible signers:

$$\text{Ring} = \{k_{\text{real}}, k_1, k_2, \ldots, k_{15}\}$$

The signature proves one of these outputs is being spent without revealing which. Current ring size is 16 (1 real + 15 decoys). The verifier knows:
- One output in the ring was spent
- Cannot determine which one
- Cannot link transactions from the same sender

For our market, this means bet transactions are unlinkable. When Alice sends 10 XMR to the market multisig, observers see a ring signature but cannot determine:
- Which of the 16 possible outputs was Alice's
- If Alice placed other bets
- Alice's wallet balance

### Multisignature Wallets

Monero multisig uses threshold cryptography. For 2-of-2:

1. **Key Generation**:

Coordinator has private key $a$, public key $A = aG$

Oracle has private key $b$, public key $B = bG$

The shared public key is computed as:
$$P = H_s(A, B) \cdot G + A + B$$

where $H_s$ is a hash-to-scalar function.

2. **Spending**:

Both parties must cooperate to spend. Each creates a partial signature:

$$\sigma_a = \text{Sign}(\text{msg}, a, r_a)$$
$$\sigma_b = \text{Sign}(\text{msg}, b, r_b)$$

The final signature combines both:
$$\sigma_{\text{final}} = \text{Combine}(\sigma_a, \sigma_b)$$

Neither party can spend alone. This prevents:
- Coordinator stealing funds (needs Oracle's signature)
- Oracle stealing funds (needs Coordinator's signature)  
- Either party losing keys (funds recoverable with both)

### Stealth Addresses

Every Monero address is actually two public keys:

$$\text{Address} = (A, B)$$

where $A$ is the public view key and $B$ is the public spend key.

When sending to an address, the sender generates a one-time address:

1. Generate random scalar $r$
2. Compute transaction public key $R = rG$  
3. Derive one-time address:
   $$P_{\text{one-time}} = H_s(rA)G + B$$

The receiver scans the blockchain by checking each output:

$$P_{\text{one-time}} \stackrel{?}{=} H_s(aR)G + B$$

where $a$ is the receiver's private view key. If the equation holds, the output belongs to them.

For our market:
- Winners provide fresh stealth addresses for payouts
- Each payout goes to a unique on-chain address
- Cannot link bet address to payout address
- Cannot identify repeat winners

## How It Works: The Technical Deep Dive

### Architecture Overview

The system has four main actors:
1. **Bettors**: Place encrypted bets, claim winnings
2. **Coordinator**: Computes payouts using FHE (trusted for liveness, not for funds)
3. **Oracle**: Reports real-world outcomes (trusted for honesty)
4. **Multisig Wallet**: Holds funds (2-of-2 between Coordinator and Oracle)

The crucial insight: the Coordinator can compute but can't steal. The Oracle can release funds but can't compute. Neither alone can run away with the money.

### Phase 1: Placing Bets

When Alice wants to bet 10 XMR on "YES":

```rust
// Alice's client encrypts her bet locally
let encrypted_outcome = FheUint8::encrypt(YES, &client_key);
let encrypted_amount = FheUint64::encrypt(10_000_000_000_000, &client_key);

// Generate a commitment for later claiming
let nonce = random_32_bytes();
let commitment = hash(nonce);
```

The commitment scheme:
$$C = H(\text{nonce} \| \text{tx\_id})$$

where $H$ is SHA3-256. This binds the bet to both a secret and the transaction.

Alice sends her XMR to the market's multisig address using a normal Monero transaction. The encrypted bet and commitment are sent to the Coordinator separately. The two can't be linked—the Monero transaction is shielded by ring signatures, while the encrypted bet is just anonymous data.

### Phase 2: Computing Payouts

After betting closes and the Oracle reports the outcome, the Coordinator computes payouts—without knowing individual bets:

```rust
// All computation happens on encrypted data
let total_winning = sum_where(encrypted_amounts, encrypted_outcomes == winner);
let total_pool = sum(encrypted_amounts);

// Calculate each person's payout
for bet in encrypted_bets {
    let is_winner = bet.outcome == winning_outcome;
    let payout = (bet.amount * total_pool) / total_winning;
    encrypted_payouts.push(if is_winner { payout } else { 0 });
}
```

Mathematically, for each bet $i$:

$$\text{payout}_i = \begin{cases}
\frac{\text{bet}_i}{\sum_j \text{bet}_j \cdot \mathbb{1}_{w_j}} \cdot \text{pool} & \text{if } \text{outcome}_i = w \\
0 & \text{otherwise}
\end{cases}$$

where $w$ is the winning outcome and $\mathbb{1}_{w_j}$ is an indicator function for winners.

The magic: these calculations happen entirely on ciphertexts. The Coordinator never sees individual bet amounts or choices.

### Phase 3: Claiming Winnings

Winners prove they won by revealing their nonce (not their identity):

```rust
// Alice proves she owns a winning bet
let claim = {
    nonce: saved_nonce,
    payout_address: fresh_stealth_address,
};

// Coordinator verifies: hash(nonce) matches a commitment
// Then decrypts only that person's payout amount
let payout = decrypt_single_slot(encrypted_payouts[index]);
```

The coordinator verifies:
$$H(\text{nonce}_{\text{claimed}} \| \text{tx\_id}) \stackrel{?}{=} C_{\text{stored}}$$

If valid, the coordinator decrypts only slot $i$ from the encrypted payout vector.

The Coordinator and Oracle jointly sign a transaction paying the winner. The funds flow from the multisig to a fresh stealth address, unlinkable to the original bet.

## The Implementation Journey

### Performance Realities

Our GPU-accelerated benchmarks on RTX 4090 hardware:
- Encrypting a bet (CPU): ~1.2ms
- FHE setup (GPU initialization): ~900ms
- GPU payout computation (10 bets): ~33.5 seconds (~3.3s per bet)
- Full market resolution (100 bets): ~56.6 seconds
  - CPU encryption: 129ms
  - GPU upload: 13ms
  - GPU computation: 56.5s
- Full market resolution (1,000 bets): ~296 seconds
  - CPU encryption: 1.3s
  - GPU upload: 130ms
  - GPU computation: 294.5s

The bottleneck isn't the homomorphic operations—it's the division operation for calculating proportional payouts. TFHE-rs handles this through circuit bootstrapping, which is computationally intensive but exact. GPU acceleration provides significant parallelization benefits for these complex FHE operations.

## Privacy Analysis: What's Hidden, What's Not

### What Stays Private
✅ **Individual bet amounts**: Hidden by FHE encryption  
✅ **Individual bet outcomes**: Hidden by FHE encryption  
✅ **Bettor identities**: Hidden by Monero's ring signatures  
✅ **Winner identities**: Payouts go to fresh stealth addresses  
✅ **Bet-to-payout linkage**: Different addresses, no on-chain connection  

### What's Public
📊 **Aggregate statistics**: Total pool, number of winners (necessary for verification)  
📊 **Market parameters**: The question, outcomes, deadlines (necessary for participation)  
📊 **Oracle decision**: Which outcome won (necessary for resolution)  

### Trust Assumptions
⚠️ **Coordinator liveness**: Must be online to compute payouts (but can't steal)  
⚠️ **Oracle honesty**: Must report correct outcomes (mitigatable with multiple oracles)  
⚠️ **No collusion**: Coordinator + Oracle together could steal funds  

The critical insight: we've separated the power to compute from the power to pay. This division of responsibility prevents unilateral theft while maintaining practical efficiency.

## Limitations

- **Coordinator sees aggregate patterns**: Statistical analysis of claiming patterns could reveal information
- **Single-threaded FHE computation**: Current implementation doesn't parallelize
- **Coordinator availability**: Funds locked if coordinator disappears before timeout
- **Trust assumptions**: Coordinator + Oracle collusion enables theft

## Code and Deployment

The complete implementation is available at: [github.com/vitorpy/monero-predict](https://github.com/vitorpy/monero-predict)

### Quick Start

**Terminal 1: Start Monero Regtest Daemon**
```bash
monerod --regtest --offline --fixed-difficulty 1 \
  --data-dir ~/.monero-regtest \
  --rpc-bind-port 18081 --p2p-bind-port 18080 \
  --rpc-bind-ip 127.0.0.1 --confirm-external-bind \
  --log-level 1
```

**Terminal 2: Start Coordinator**
```bash
cargo run --release --bin monero-predict
```

**Terminal 3: Run Full Test**
```bash
./test_full_flow.sh
```

This creates a market, generates wallets, mines blocks, and demonstrates the complete flow.

### Place a Bet

```bash
cargo run --bin bettor -- bet \
  --market-id btc-100k-2025 \
  --outcome YES \
  --amount 10.5
```

This will:
1. Generate/load FHE client keys
2. Encrypt your bet (outcome + amount)
3. Save a nonce file for claiming later
4. Submit encrypted bet to coordinator

### Claim Winnings

After the market resolves:

```bash
cargo run --bin bettor -- claim \
  --market-id btc-100k-2025 \
  --nonce-file bet_<commitment>.nonce \
  --payout-address <your-monero-address>
```

### Running Your Own Market

1. **Start Monero daemon** (regtest for testing, mainnet for production)
2. **Setup Monero multisig** (2-of-2 between coordinator and oracle)
3. **Start the coordinator** (`cargo run --release --bin monero-predict`)
4. **Create your market** via API (`POST /market/create`)
5. **Share with bettors** and collect encrypted bets
6. **Oracle resolves** via API (`POST /market/:id/resolve`)
7. **Winners claim** using their saved nonce files

## Conclusion

That's all, folks.

Code is open source at: [github.com/vitorpy/monero-predict](https://github.com/vitorpy/monero-predict)

