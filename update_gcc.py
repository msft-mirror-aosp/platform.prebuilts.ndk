#!/usr/bin/env python
#
# Copyright (C) 2015 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Update the prebuilt NDK GCC from the build server."""
from __future__ import print_function

import argparse
import inspect
import logging
import os
import site
import sys

site.addsitedir(os.path.join(os.path.dirname(__file__), '../../ndk/build/lib'))

import build_support  # pylint: disable=import-error


def logger():
    """Returns the module logger."""
    return logging.getLogger(__name__)


def check_call(cmd):
    """subprocess.check_call with logging."""
    import subprocess
    logger().debug('check_call `%s`', ' '.join(cmd))
    subprocess.check_call(cmd)


def rmtree(path):
    """shutil.rmtree with logging."""
    import shutil
    logger().debug('rmtree %s', path)
    shutil.rmtree(path)


def makedirs(path):
    """os.makedirs with logging."""
    logger().debug('mkdir -p %s', path)
    os.makedirs(path)


def remove(path):
    """os.remove with logging."""
    logger().debug('rm %s', path)
    os.remove(path)


def parse_args():
    """Parse and return command line arguments."""
    parser = argparse.ArgumentParser(
        description=inspect.getdoc(sys.modules[__name__]))

    parser.add_argument(
        'build', metavar='BUILD',
        help='Build number to pull from the build server.')

    parser.add_argument(
        '--branch', default='aosp-gcc',
        help='Branch to pull from the build server.')

    parser.add_argument(
        '--use-current-branch', action='store_true',
        help='Do not repo start a new branch for the update.')

    return parser.parse_args()


def build_name(host, arch):
    """Gets the release build name for an NDK host tag.

    The builds are named by a short identifier like "linux" or "win64".

    >>> build_name('darwin-x86_64', 'arm')
    'arm'

    >>> build_name('windows', 'x86')
    'win_x86'
    """
    if host == 'darwin-x86_64':
        return arch + '_mac'

    return {
        'linux-x86_64': 'linux',
        'windows': 'win',
        'windows-x86_64': 'win64',
    }[host] + '_' + arch


def package_name(host, arch):
    """Returns the file name for a given package configuration.

    >>> package_name('linux-x86_64', 'arm')
    'gcc-arm-linux-x86_64.tar.bz2'

    >>> package_name('windows', 'x86')
    'gcc-x86-windows.tar.bz2'
    """
    return 'gcc-{}-{}.tar.bz2'.format(arch, host)


def fetch_artifact(branch, target, build, pattern):
    """Fetches an artifact from the build server."""
    fetch_artifact_path = '/google/data/ro/projects/android/fetch_artifact'
    cmd = [fetch_artifact_path, '--branch', branch, '--target=' + target,
           '--bid', build, pattern]
    check_call(cmd)

    # Fetch artifact dumps crap to the working directory.
    remove('.fetch_artifact2.dat')


def download_build(branch, host, arch, build_number):
    """Download a build from the build server."""
    pkg_name = package_name(host, arch)
    fetch_artifact(branch, build_name(host, arch), build_number, pkg_name)
    return pkg_name


def extract_package(package, host, install_dir):
    """Extract the downloaded toolchain."""
    host_dir = os.path.join(install_dir, 'toolchains', host)
    if not os.path.exists(host_dir):
        makedirs(host_dir)

    cmd = ['tar', 'xf', package, '-C', host_dir]
    check_call(cmd)


def main():
    """Program entry point."""
    logging.basicConfig(level=logging.DEBUG)

    args = parse_args()

    os.chdir(os.path.realpath(os.path.dirname(__file__)))

    if not args.use_current_branch:
        check_call(['repo', 'start', 'update-gcc-{}'.format(args.build), '.'])

    hosts = ('darwin-x86_64', 'linux-x86_64', 'windows', 'windows-x86_64')
    packages = []
    for host in hosts:
        for arch in build_support.ALL_ARCHITECTURES:
            if arch.startswith('mips'):
                continue
            package = download_build(args.branch, host, arch, args.build)
            packages.append((host, arch, package))

    install_dir = 'current'
    install_subdir = os.path.join(install_dir, 'toolchains')

    for host, arch, package in packages:
        toolchain = build_support.arch_to_toolchain(arch) + '-4.9'
        toolchain_path = os.path.join(install_subdir, host, toolchain)
        if os.path.exists(toolchain_path):
            logger().info('Removing old %s %s...', host, toolchain)
            check_call(
                ['git', 'rm', '-rf', '--ignore-unmatch', toolchain_path])

            # Git doesn't believe in directories, so `git rm -rf` might leave
            # behind empty directories.
            if os.path.isdir(toolchain_path):
                rmtree(toolchain_path)

        if not os.path.exists(install_subdir):
            makedirs(install_subdir)

        logger().info('Extracting %s...', package)
        extract_package(package, host, install_dir)

        logger().info('Adding %s %s files to index...', host, toolchain)
        check_call(['git', 'add', toolchain_path])

    logger().info('Committing update...')
    message = 'Update prebuilt GCC to build {}.'.format(args.build)
    check_call(['git', 'commit', '-m', message])


if __name__ == '__main__':
    main()
