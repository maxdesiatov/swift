#/bin/bash

set -ex
SOURCE_PATH="$(cd "$(dirname $0)/../../.." && pwd)"
UTILS_PATH="$(cd "$(dirname $0)" && pwd)"

WASI_SDK_PATH=$SOURCE_PATH/wasi-sdk

case $(uname -s) in
  Darwin)
    OS_SUFFIX=osx
    HOST_PRESET=webassembly-host
  ;;
  Linux)
    OS_SUFFIX=ubuntu18.04
    HOST_PRESET=webassembly-linux-host
  ;;
  *)
    echo "Unrecognised platform $(uname -s)"
    exit 1
  ;;
esac

YEAR=$(date +"%Y")
MONTH=$(date +"%m")
DAY=$(date +"%d")
TOOLCHAIN_VERSION="${YEAR}${MONTH}${DAY}"
TOOLCHAIN_NAME="swift-wasm-host-DEVELOPMENT-SNAPSHOT-${YEAR}-${MONTH}-${DAY}-a"
ARCHIVE="${TOOLCHAIN_NAME}-${OS_SUFFIX}.tar.gz"
INSTALLABLE_PACKAGE=$SOURCE_PATH/$ARCHIVE

PACKAGE_ARTIFACT="$SOURCE_PATH/swift-wasm-host-DEVELOPMENT-SNAPSHOT-${OS_SUFFIX}.tar.gz"

HOST_TOOLCHAIN_DESTDIR=$SOURCE_PATH/host-toolchain-sdk

# Avoid clang headers symlink issues
mkdir -p $HOST_TOOLCHAIN_SDK/usr/lib/clang/10.0.0

# Build the host toolchain and SDK first.
$SOURCE_PATH/swift/utils/build-script \
  --preset=$HOST_PRESET \
  INSTALL_DESTDIR="$HOST_TOOLCHAIN_DESTDIR" \
  TOOLCHAIN_NAME="$TOOLCHAIN_NAME" \
  C_CXX_LAUNCHER="$(which sccache)"

cd $HOST_TOOLCHAIN_DESTDIR
tar cfz $PACKAGE_ARTIFACT $TOOLCHAIN_NAME
