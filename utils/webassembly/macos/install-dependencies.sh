#/bin/bash

set -ex

brew uninstall python@2 || true
brew install cmake ninja llvm sccache wasmer

SOURCE_PATH="$( cd "$(dirname $0)/../../../../" && pwd  )"
SWIFT_PATH=$SOURCE_PATH/swift
cd $SWIFT_PATH

./utils/update-checkout --clone --scheme wasm --skip-repository swift
