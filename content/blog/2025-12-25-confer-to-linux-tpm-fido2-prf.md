---
date: "2025-12-25T00:00:00Z"
tags:
  - linux
  - security
  - webauthn
  - fido2
  - tpm
  - privacy
  - encryption
title: Making Confer.to Work on Linux with TPM-backed WebAuthn
mermaid: true
---

[Confer.to](https://confer.to) is an end-to-end encrypted AI chat service. Unlike typical AI assistants where your conversations feed into corporate training data, Confer uses the WebAuthn PRF extension to derive encryption keys directly from your fingerprint. No passwords, no server-side key storage—just your biometric tied to a hardware-backed credential.

There's a catch: this requires a **platform authenticator** with PRF support. Windows Hello and macOS Touch ID work out of the box. Linux? Not so much.

## The Problem: Linux Has No Platform Authenticator

WebAuthn distinguishes between two types of authenticators:

- **Platform authenticators**: Built into your device (Windows Hello, Touch ID, Android biometrics)
- **Roaming authenticators**: External hardware like YubiKeys

Linux has excellent support for roaming authenticators via USB/NFC. But platform authenticators? The browser expects something that simply doesn't exist in the standard Linux stack.

You might think "I'll just use my YubiKey." Unfortunately, most hardware security keys don't support the PRF extension. Even the YubiKey 5 series, which supports CTAP2.1 and `hmac-secret`, doesn't expose PRF to the browser in a way that works for client-side encryption use cases.

## The PRF Extension: Deriving Keys from Credentials

The PRF (Pseudo-Random Function) extension solves a specific problem: how do you derive cryptographic material from a WebAuthn credential without storing secrets anywhere?

Here's how it works:

1. Website provides a **salt** (32 bytes)
2. Authenticator uses credential-specific secret material
3. Authenticator computes `HMAC-SHA256(credRandom, salt)` → 32-byte output
4. Website uses this output as an encryption key

The magic: **same credential + same salt = same key, every time**. No password to remember, no key to store. Your fingerprint *is* the key derivation mechanism.

## The Solution: TPM-FIDO2-PRF

I built a two-component system that creates a platform authenticator for Linux:

- **[tpm-fido2-prf](https://github.com/vitorpy/tpm-fido2-prf)**: A native Go application that implements FIDO2/CTAP2 using your system's TPM
- **[tpm-fido2-extension](https://github.com/vitorpy/tpm-fido2-extension)**: A Chrome extension that intercepts WebAuthn API calls

Together, they make the browser believe it has a built-in platform authenticator with full PRF support.

### Architecture Overview

<pre class="mermaid">
sequenceDiagram
participant W as Website
participant I as inject.js
participant C as content.js
participant B as background.js
participant N as tpm-fido
participant F as fprintd
participant T as TPM
W->>I: credentials.create
I->>C: postMessage
C->>B: sendMessage
B->>N: Native Messaging
N->>F: Verify fingerprint
F-->>N: User verified
N->>T: Generate key
T-->>N: Key handle
N->>N: Compute PRF
N-->>B: Attestation + PRF
B-->>C: Response
C-->>I: postMessage
I-->>W: PublicKeyCredential
</pre>

<noscript>

**Text fallback** (JavaScript disabled):
```
Website → inject.js → content.js → background.js → tpm-fido → fprintd → TPM
                                                              ↓
Website ← inject.js ← content.js ← background.js ← tpm-fido ← PRF + attestation
```
</noscript>

## Deep Dive: How It Works

### Chrome Extension Architecture

The extension uses three layers to intercept WebAuthn:

1. **inject.js** (page context): Overrides `navigator.credentials.create()` and `navigator.credentials.get()`. Serializes `ArrayBuffer` objects to Base64 for JSON transport.

2. **content.js** (isolated world): Bridges between page context and extension via `window.postMessage` and `chrome.runtime.sendMessage`.

3. **background.js** (service worker): Communicates with the native host via Chrome's Native Messaging API.

The extension also overrides `PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()` to return `true`, making websites believe a platform authenticator exists.

### TPM Key Derivation

This is the clever part. The TPM backend uses HKDF to derive unique keys per relying party:

```go
// From tpm/tpm.go
info := append([]byte("tpm-fido-application-key"), applicationParam...)
r := hkdf.New(sha256.New, seed, []byte{}, info)
```

On registration:
1. Generate a random 20-byte seed
2. Derive a primary key template using HKDF with the seed + RP ID hash
3. Create a TPM primary key under the Owner hierarchy
4. Generate a signing child key from the primary
5. Return handle: `[child_private_blob | child_public_blob | seed]`

On authentication:
1. Extract seed from the handle
2. Reconstruct the primary key using the same HKDF derivation
3. Load the child key from the handle
4. Sign the challenge

**Why this works**: The TPM cryptographically binds the child key to its parent. If the seed is wrong, the parent reconstruction fails, and the child key can't be loaded. Keys can't be extracted or used on a different TPM.

### PRF Implementation

During credential creation, PRF outputs are computed immediately:

```go
// Salt hashing per WebAuthn spec
hashedSalt := sha256.Sum256(append([]byte("WebAuthn PRF\x00"), salt...))

// Derive credential-specific random
credRandom := hmac.New(sha256.New, seed)
credRandom.Write([]byte("credential-random"))

// Compute PRF output
output := hmac.New(sha256.New, credRandom.Sum(nil))
output.Write(hashedSalt[:])
// output.Sum(nil) is the 32-byte PRF result
```

The website receives this output and can use it directly as an AES key for encryption.

### User Verification via Fingerprint

Every operation requires fingerprint verification:

```go
// Spawn fprintd-verify and wait for result
cmd := exec.Command("fprintd-verify")
// ... handle result
```

A desktop notification prompts the user to touch the fingerprint reader. This satisfies the "user verification" requirement of WebAuthn.

## Setup Guide

### Prerequisites

1. **TPM 2.0**: Check with `ls /dev/tpmrm0`
2. **TPM access**: Add yourself to the `tss` group:
   ```bash
   sudo usermod -aG tss $USER
   # Log out and back in
   ```
3. **Fingerprint reader**: Must be supported by fprintd
4. **Enrolled fingerprint**:
   ```bash
   fprintd-enroll
   ```
5. **Go 1.21+**: For building the native component
6. **Chrome or Chromium**

### Clone and Build

```bash
# Clone both repos
git clone https://github.com/vitorpy/tpm-fido2-prf.git
git clone https://github.com/vitorpy/tpm-fido2-extension.git

# Build native component
cd tpm-fido2-prf
go build -o ~/bin/tpm-fido .
```

### Load the Chrome Extension

1. Open Chrome → `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked" → select the `tpm-fido2-extension` directory
4. The extension ID should be `bfmfknknibchmioeamgbnlpakcjimnbf` (stable, derived from manifest key)

### Configure Native Messaging

```bash
cd tpm-fido2-extension
./setup.sh
```

This creates `~/.config/google-chrome/NativeMessagingHosts/com.vitorpy.tpmfido.json`:

```json
{
  "name": "com.vitorpy.tpmfido",
  "description": "TPM-FIDO WebAuthn Platform Authenticator with PRF support",
  "path": "/home/youruser/bin/tpm-fido",
  "type": "stdio",
  "allowed_origins": ["chrome-extension://bfmfknknibchmioeamgbnlpakcjimnbf/"]
}
```

### Test the Setup

1. Restart Chrome
2. Visit [webauthn.io](https://webauthn.io)
3. Register a credential → fingerprint prompt should appear
4. Authenticate → verify it works

**Debug**: `chrome://extensions` → TPM-FIDO2 → "Inspect views: service worker"

### Using with Confer.to

Once set up, navigate to [confer.to](https://confer.to) and login. The platform authenticator will be used automatically.

## Security Considerations

- **Private keys never leave the TPM**: Only the TPM can sign; key material is hardware-protected
- **Fingerprint required for every operation**: No silent authentication
- **Credential metadata stored locally**: Only user info and credential IDs at `~/.local/share/tpm-fido/credentials.json`—not keys
- **Self-signed attestation**: Uses a generic certificate to avoid device fingerprinting (privacy trade-off vs. strict RP requirements)

## Limitations

- **Chrome/Chromium only**: No Firefox WebExtension port (yet)
- **Requires fprintd**: No alternative user verification methods
- **Self-signed attestation**: Some strict relying parties may reject credentials without hardware attestation

## Repository Links

- [tpm-fido2-prf](https://github.com/vitorpy/tpm-fido2-prf) - Native TPM-backed authenticator
- [tpm-fido2-extension](https://github.com/vitorpy/tpm-fido2-extension) - Chrome extension
- [Confer.to](https://confer.to) - E2E encrypted AI chat
- [Confessions to a Data Lake](https://confer.to/blog/2025/12/confessions-to-a-data-lake/) - Confer's privacy philosophy
