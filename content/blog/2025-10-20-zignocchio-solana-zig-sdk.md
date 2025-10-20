---
date: "2025-10-20T00:00:00Z"
tags:
- solana
- zig
- blockchain
title: Zignocchio - Building Solana Programs in Zig
---

[Zignocchio](https://github.com/vitorpy/zignocchio) is a zero-dependency SDK for writing Solana programs in Zig. It uses the standard BPF target and [sbpf-linker](https://github.com/blueshift-gg/sbpf-linker) to compile Zig code to Solana's eBPF bytecode.


## Prerequisites

```bash
# Install sbpf-linker from master (includes latest fixes)
cargo install --git https://github.com/blueshift-gg/sbpf-linker.git

# Install Zig 0.15.2 or later
```

## Hello World Program

Here's a minimal Solana program that logs a message:

```zig
const sdk = @import("sdk/zignocchio.zig");

export fn entrypoint(input: [*]u8) u64 {
    return @call(.always_inline, sdk.createEntrypoint(processInstruction), .{input});
}

fn processInstruction(
    program_id: *const sdk.Pubkey,
    accounts: []sdk.AccountInfo,
    instruction_data: []const u8,
) sdk.ProgramResult {
    sdk.logMsg("Hello from Zignocchio!");
    return .{};
}
```

The `createEntrypoint` function deserializes Solana's input buffer into typed parameters. It uses zero-copy deserialization - no allocations occur.

## Build Configuration

Create `build.zig`:

```zig
const std = @import("std");

pub fn build(b: *std.Build) !void {
    const optimize = .ReleaseSmall;

    // Step 1: Generate LLVM bitcode
    const bitcode_path = "entrypoint.bc";
    const gen_bitcode = b.addSystemCommand(&.{
        "zig",
        "build-lib",
        "-target",
        "bpfel-freestanding",
        "-O",
        "ReleaseSmall",
        "-femit-llvm-bc=" ++ bitcode_path,
        "-fno-emit-bin",
        "src/main.zig",
    });

    // Step 2: Link with sbpf-linker
    const program_so_path = "zig-out/lib/program.so";
    const link_program = b.addSystemCommand(&.{
        "sbpf-linker",
        "--cpu", "v2",
        "--export", "entrypoint",
        "-o", program_so_path,
        bitcode_path,
    });
    link_program.step.dependOn(&gen_bitcode.step);

    b.getInstallStep().dependOn(&link_program.step);
}
```

Build with:

```bash
zig build
```

This generates `zig-out/lib/program.so` ready for deployment.

## How It Works

Zig compiles to LLVM bitcode with `-femit-llvm-bc`. sbpf-linker transforms this bitcode into Solana's eBPF format. The `--cpu v2` flag ensures compatibility with Solana's sBPF instruction set.

Solana syscalls are invoked via function pointers with MurmurHash3-32 hashes:

```zig
const syscalls = @import("syscalls.zig");
syscalls.log(&message);  // Calls sol_log_ via hash 0x207559bd
```

## Repository

Source code and examples: [github.com/vitorpy/zignocchio](https://github.com/vitorpy/zignocchio)

The SDK includes working counter and hello world examples with Jest tests that run against solana-test-validator.
