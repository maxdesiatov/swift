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

but LLVM Linker does not support it diretly yet.

## What do you need

get the latest source code with the `next` scheme, so that you are picking up the latest LLVM.

```
utils/update-checkout --clone --scheme next
```

Then, you need to build LLVM and Clang:
```
utils/build-script -webassembly
```

Once you have the toolchain built, you can start building dependencies.

You will need to create a folder that's the sysroot. I chose `sysroot` under `swift-source` folder.

### musl (aka libc)
Musl seems to be the implemenation of choice in the WebAssembly community.

You will need Musl that supports WebAssembly. Unfornately, that has not been upstreamed to musl proper. 
I have been using the version from here: https://github.com/NWilson/musl/tree/musl-wasm-native

`LLVM_PATH` is the path where LLVM was built. It should under `build/Ninja-RelWithDebInfoAssert/llvm-macosx-x86_64` (if you are building on macOS with RelWithDebInfo)

`SYSROOT` is the path where all the dependencies would be copied to.

```
#!/bin/sh
export CC=${LLVM_PATH}/bin/clang
export CFLAGS=--target=wasm32-unknown-unknow-wasm
export CROSS_COMPILE=${LLVM_PATH}/bin/llvm-

./configure --target=wasm32 --prefix=/ --exec_prefix=/ --disable-shared

echo DESTDIR=${SYSROOT} >> config.mak
make install
```

### compiler-rt

### libcxx

### ICU4C

`WORKSPACE` is your swift-source folder

`BUILD_DIR` and `LLVM_BIN` might need to be adjusted if you are building on different machine and different configurations

```
#!/bin/sh
BUILD_DIR=${WORKSPACE}/build/Ninja-RelWithDebInfoAssert
LLVM_BIN="${BUILD_DIR}/llvm-macosx-x86_64/bin"

LIBICU_SOURCE_DIR=${WORKSPACE}/icu

function build_directory() {
    host=$1
    product=$2
    echo "${BUILD_DIR}/${product}-${host}"
}

SWIFT_HOST_VARIANT=webassembly
SWIFT_HOST_VARIANT_ARCH=wasm32
host=macosx-x86_64
product=libicu
SWIFT_BUILD_PATH=$(build_directory ${host} swift)
LIBICU_BUILD_DIR=$(build_directory "${SWIFT_HOST_VARIANT}-${SWIFT_HOST_VARIANT_ARCH}" ${product})
ICU_TMPINSTALL=${LIBICU_BUILD_DIR}/tmp_install
ICU_TMPLIBDIR="${SWIFT_BUILD_PATH}/lib/swift/${SWIFT_HOST_VARIANT}/${SWIFT_HOST_VARIANT_ARCH}"

mkdir -p ${LIBICU_BUILD_DIR}
mkdir -p ${ICU_TMPINSTALL}
icu_build_variant_arg="--enable-release"
cd ${LIBICU_BUILD_DIR}
CC="${LLVM_BIN}/clang" CXX="${LLVM_BIN}/clang++" ${LIBICU_SOURCE_DIR}/source/configure \
    ${icu_build_variant_arg} \
    --host=${SWIFT_HOST_VARIANT_ARCH}-linux \
    --prefix=${ICU_TMPINSTALL} \
    --libdir=${ICU_TMPLIBDIR} \
    --enable-static \
    --disable-shared \
    --enable-strict \
    --disable-icuio \
    --disable-plugins \
    --disable-dyload \
    --disable-extras \
    --disable-samples
cd ${LIBICU_BUILD_DIR}
make install

ICU_LIBDIR="$(build_directory ${host} swift)/lib/swift/${SWIFT_HOST_VARIANT}/${SWIFT_HOST_VARIANT_ARCH}"
ICU_LIBDIR_STATIC="$(build_directory ${host} swift)/lib/swift_static/${SWIFT_HOST_VARIANT}"
ICU_LIBDIR_STATIC_ARCH="$(build_directory ${host} swift)/lib/swift_static/${SWIFT_HOST_VARIANT}/${SWIFT_HOST_VARIANT_ARCH}"
mkdir -p "${ICU_LIBDIR_STATIC_ARCH}"

# Copy the static libs into the swift_static directory
for l in uc i18n data
do
    lib="${ICU_LIBDIR}/libicu${l}.a"
    cp "${lib}" "${ICU_LIBDIR_STATIC}"
    cp "${lib}" "${ICU_LIBDIR_STATIC_ARCH}"
done
```

Once you have all those, you are ready build the rest of swift.

