---
layout: post
title: A Tact primer for Solidity developers
tags: [git, tutorial, github]
---

## Introduction

Lorem ipsum

```mermaid
flowchart TD
    A[Christmas] -->|Get money| B(Go shopping)
    B --> C{Let me think}
    C -->|One| D[Laptop]
    C -->|Two| E[iPhone]
    C -->|Three| F[fa:fa-car Car]
```

```tact
message (0x123123) TransferMsg {
  to: Address;
  text: String;
}

contract SimpleContract {
  init() {}
  receive() {}
  receive(msg: TransferMsg) {
      send(SendParameters{
          to: msg.to,
          value: 0,
          mode: SendRemainingValue,
          body: msg.text.asComment()
      });
  }
}
```
