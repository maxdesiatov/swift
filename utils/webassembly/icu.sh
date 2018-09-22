#!/bin/sh

WORKSPACE=$1

BUILD_DIR=$2
N_JOBS=$3

LLVM_BIN="${BUILD_DIR}/llvm-macosx-x86_64/bin"

LIBICU_SOURCE_DIR=${WORKSPACE}/icu/icu4c

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
make -j${N_JOBS}
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
