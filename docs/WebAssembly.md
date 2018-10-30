# Getting Started with Swift on WebAssembly

Currently the port is still work-in-progress. 
I am able to compile enough of the source code to generate a .swiftModule file. 
But currently still require work to compile a .swift file.

## Known issues

In generaly, WebAssembly itself and LLVM's support for it are both evolving.

In terms of changes, WASM-support involves a new architecture/opcodes, new object file format. And LLVM support is still being filled out.

### Threading is not there yet.
https://github.com/WebAssembly/design/issues/1073

atomic op codes are in design phase.

ThreadLocal storage and pthread is not ready yet.

I had to disable some stuff just to compile `stdlib/public/runtime/Exclusivity.cpp`.

### Wasm Object File Format
I was running into issues with how Sections are being written for Wasm Object Format.

https://bugs.llvm.org/show_bug.cgi?id=35928

Also alignment issues.

### AsmParser does not exist
Swift Runtime is currently not yet implemented because of a WASM MCAsmParser does not exist yet.

https://bugs.llvm.org/show_bug.cgi?id=34544

### Dynamic Library

The spec is there http://webassembly.org/docs/dynamic-linking/

But LLVM Linker does not support it diretly yet.

## What do you need

Get the latest source code with the `wasm-next` scheme, so that you are picking up the latest LLVM and clang.

```
./swift/utils/update-checkout --clone --scheme wasm-next --target-platform WebAssembly
```

Then you need to run the build script.
```
./swift/utils/build-script --skip-build-benchmarks --webassembly --libicu
```
