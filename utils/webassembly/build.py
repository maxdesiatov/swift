#! /usr/bin/env python

import os
import proc
import shutil
import sys
from file_util import Chdir, CopyTree, Mkdir, Remove

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.path.join(SCRIPT_DIR, '../../..')

BUILD_ROOT_DIR = os.path.join(WORK_DIR, 'build/Ninja-DebugAssert+stdlib-RelWithDebInfoAssert')

MUSL_SRC_DIR = os.environ['MUSL_SOURCE_DIR']
MUSL_OUT_DIR = os.environ['MUSL_BUILD_DIR']

LLVM_SRC_DIR = os.path.join(WORK_DIR, 'libcxx')

LIBCXX_SRC_DIR = os.path.join(WORK_DIR, 'libcxx')
LIBCXXABI_SRC_DIR = os.path.join(WORK_DIR, 'libcxxabi')
LIBCXX_OUT_DIR = os.path.join(BUILD_ROOT_DIR, 'libcxx')
LIBCXXABI_OUT_DIR = os.path.join(BUILD_ROOT_DIR, 'libcxxabi')

COMPILER_RT_SRC_DIR = os.path.join(WORK_DIR, 'compiler-rt')
COMPILER_RT_OUT_DIR = os.path.join(BUILD_ROOT_DIR, 'compiler-rt')

INSTALL_SYSROOT = os.path.join(BUILD_ROOT_DIR, 'sysroot')
INSTALL_DIR = os.path.join(BUILD_ROOT_DIR, 'wasm')

LLVM_OUT_DIR = os.path.join(BUILD_ROOT_DIR, 'llvm-macosx-x86_64')
LLVM_VERSION = '7.0.0'
INSTALL_BIN = os.path.join(WORK_DIR, LLVM_OUT_DIR, 'bin')

CLANG_BIN_PATH = os.path.join(INSTALL_BIN, 'clang')
LLVM_AR_BIN_PATH = os.path.join(INSTALL_BIN, 'llvm-ar')
LLVM_RANLIB_BIN_PATH = os.path.join(INSTALL_BIN, 'llvm-ranlib')

WASM_TRIPLE = 'wasm32-unknown-unknown-wasm'

PREBUILT_CMAKE_BIN = '/usr/local/bin/cmake'

Mkdir(INSTALL_SYSROOT)

def IsWindows():
  return sys.platform == 'win32'


def IsLinux():
  return sys.platform == 'linux2'


def IsMac():
  return sys.platform == 'darwin'

def Executable(name, extension='.exe'):
  return name + extension if IsWindows() else name

def CopyLibraryToSysroot(library):
  """All libraries are archived in the same tar file."""
  install_lib = os.path.join(INSTALL_SYSROOT, 'lib')
  print 'Copying library %s to archive %s' % (library, install_lib)
  Mkdir(install_lib)
  shutil.copy2(library, install_lib)

def CopyLibraryToArchive(library, prefix=''):
  """All libraries are archived in the same tar file."""
  install_lib = os.path.join(INSTALL_DIR, prefix, 'lib')
  print 'Copying library %s to archive %s' % (library, install_lib)
  Mkdir(install_lib)
  shutil.copy2(library, install_lib)

def CompilerRT():
  # TODO(sbc): Remove this.
  # The compiler-rt doesn't currently rebuild libraries when a new -DCMAKE_AR
  # value is specified.
  if os.path.isdir(COMPILER_RT_OUT_DIR):
    Remove(COMPILER_RT_OUT_DIR)

  Mkdir(COMPILER_RT_OUT_DIR)
  command = [PREBUILT_CMAKE_BIN, '-G', 'Ninja',
             os.path.join(COMPILER_RT_SRC_DIR, 'lib', 'builtins'),
             '-DCMAKE_C_COMPILER_WORKS=ON',
             '-DCOMPILER_RT_BAREMETAL_BUILD=On',
             '-DCOMPILER_RT_BUILD_XRAY=OFF',
             '-DCOMPILER_RT_INCLUDE_TESTS=OFF',
             '-DCOMPILER_RT_ENABLE_IOS=OFF',
             '-DCOMPILER_RT_DEFAULT_TARGET_ONLY=On',
             '-DLLVM_CONFIG_PATH=' +
             Executable(os.path.join(LLVM_OUT_DIR, 'bin', 'llvm-config')),
             '-DCOMPILER_RT_OS_DIR=.',
             '-DCMAKE_INSTALL_PREFIX=' +
             os.path.join(LLVM_OUT_DIR, 'lib', 'clang', LLVM_VERSION),
             '-DCMAKE_C_COMPILER=' + CLANG_BIN_PATH,
             '-DCMAKE_CXX_COMPILER=' + CLANG_BIN_PATH,
             '-DCMAKE_C_COMPILER_TARGET=' + WASM_TRIPLE,
             '-DCMAKE_CXX_COMPILER_TARGET=' + WASM_TRIPLE,
             '-DCMAKE_AR=' + LLVM_AR_BIN_PATH,
             '-DCMAKE_RANLIB=' + LLVM_RANLIB_BIN_PATH,
             '-DCMAKE_SYSROOT=' + INSTALL_SYSROOT]

  proc.check_call(command, cwd=COMPILER_RT_OUT_DIR)
  proc.check_call(['ninja', '-v'], cwd=COMPILER_RT_OUT_DIR)
  proc.check_call(['ninja', 'install'], cwd=COMPILER_RT_OUT_DIR)

def LibCXX():
  if os.path.isdir(LIBCXX_OUT_DIR):
    Remove(LIBCXX_OUT_DIR)
  Mkdir(LIBCXX_OUT_DIR)
  command = [PREBUILT_CMAKE_BIN, '-G', 'Ninja', os.path.join(LIBCXX_SRC_DIR),
             '-DCMAKE_EXE_LINKER_FLAGS=-nostdlib++',
             '-DLIBCXX_ENABLE_THREADS=OFF',
             '-DLIBCXX_ENABLE_SHARED=OFF',
             '-DLIBCXX_HAS_MUSL_LIBC=ON',
             '-DLIBCXX_CXX_ABI=libcxxabi',
             '-DLIBCXX_CXX_ABI_INCLUDE_PATHS=' +
             os.path.join(LIBCXXABI_SRC_DIR, 'include'),
             '-DLLVM_PATH=' + LLVM_SRC_DIR,]
            #  '-DCMAKE_TOOLCHAIN_FILE=' + CMAKE_TOOLCHAIN_FILE]

  proc.check_call(command, cwd=LIBCXX_OUT_DIR)
  proc.check_call(['ninja', '-v'], cwd=LIBCXX_OUT_DIR)
  proc.check_call(['ninja', 'install'], cwd=LIBCXX_OUT_DIR)

def LibCXXABI():
  if os.path.isdir(LIBCXXABI_OUT_DIR):
    Remove(LIBCXXABI_OUT_DIR)
  Mkdir(LIBCXXABI_OUT_DIR)
  command = [PREBUILT_CMAKE_BIN, '-G', 'Ninja',
             os.path.join(LIBCXXABI_SRC_DIR),
             '-DCMAKE_EXE_LINKER_FLAGS=-nostdlib++',
             '-DLIBCXXABI_ENABLE_SHARED=OFF',
             '-DLIBCXXABI_ENABLE_THREADS=OFF',
             # HandleLLVMOptions.cmake include CheckCompilerVersion.cmake.
             # This checks for working <atomic> header, which in turn errors
             # out on systems with threads disabled
             '-DLLVM_COMPILER_CHECKED=ON',
             '-DLIBCXXABI_LIBCXX_PATH=' + LIBCXX_SRC_DIR,
             '-DLIBCXXABI_LIBCXX_INCLUDES=' +
             os.path.join(INSTALL_SYSROOT, 'include', 'c++', 'v1'),
             '-DLLVM_PATH=' + LLVM_SRC_DIR,
             '-DCMAKE_C_COMPILER=' + CLANG_BIN_PATH,
             '-DCMAKE_CXX_COMPILER=' + CLANG_BIN_PATH,
             '-DCMAKE_C_COMPILER_TARGET=' + WASM_TRIPLE,
             '-DCMAKE_CXX_COMPILER_TARGET=' + WASM_TRIPLE,
             '-DCMAKE_AR=' + LLVM_RANLIB_BIN_PATH,
             '-DCMAKE_RANLIB=' + LLVM_AR_BIN_PATH,
             '-DCMAKE_SYSROOT=' + INSTALL_SYSROOT]

  proc.check_call(command, cwd=LIBCXXABI_OUT_DIR)
  proc.check_call(['ninja', '-v'], cwd=LIBCXXABI_OUT_DIR)
  proc.check_call(['ninja', 'install'], cwd=LIBCXXABI_OUT_DIR)
  CopyLibraryToSysroot(os.path.join(SCRIPT_DIR, 'libc++abi.imports'))

def Musl():
  Mkdir(MUSL_OUT_DIR)
  # Build musl directly to wasm object files in an ar library
  proc.check_call([
      os.path.join(MUSL_SRC_DIR, 'libc.py'),
      '--clang_dir', INSTALL_BIN,
      '--binaryen_dir', os.path.join(INSTALL_BIN),
      '--sexpr_wasm', os.path.join(INSTALL_BIN, 'wat2wasm'),
      '--out', os.path.join(MUSL_OUT_DIR, 'libc.a'),
      '--musl', MUSL_SRC_DIR, '--compile-to-wasm'])
  AR = os.path.join(INSTALL_BIN, 'llvm-ar')
  proc.check_call([AR, 'rc', os.path.join(MUSL_OUT_DIR, 'libm.a')])
  CopyLibraryToSysroot(os.path.join(MUSL_OUT_DIR, 'libc.a'))
  CopyLibraryToSysroot(os.path.join(MUSL_OUT_DIR, 'libm.a'))
  CopyLibraryToSysroot(os.path.join(MUSL_OUT_DIR, 'crt1.o'))
  CopyLibraryToSysroot(os.path.join(MUSL_SRC_DIR, 'arch', 'wasm32',
                                    'libc.imports'))

  wasm_js = os.path.join(MUSL_SRC_DIR, 'arch', 'wasm32', 'wasm.js')
  CopyLibraryToArchive(wasm_js)

  CopyTree(os.path.join(MUSL_SRC_DIR, 'include'),
            os.path.join(INSTALL_SYSROOT, 'include'))
  CopyTree(os.path.join(MUSL_SRC_DIR, 'arch', 'generic', 'bits'),
            os.path.join(INSTALL_SYSROOT, 'include', 'bits'))
  CopyTree(os.path.join(MUSL_SRC_DIR, 'arch', 'wasm32', 'bits'),
            os.path.join(INSTALL_SYSROOT, 'include', 'bits'))
  CopyTree(os.path.join(MUSL_OUT_DIR, 'obj', 'include', 'bits'),
            os.path.join(INSTALL_SYSROOT, 'include', 'bits'))

Musl()
