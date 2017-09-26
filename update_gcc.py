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
import os
import shutil
import site
import subprocess
import sys

site.addsitedir(os.path.join(os.path.dirname(__file__), '../../ndk/build/lib'))

import build_support  # pylint: disable=import-error


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


def host_to_build_host(host):
    """Gets the build host name for an NDK host tag.

    The Windows builds are done from Linux.
    """
    return {
        'darwin-x86_64': 'mac',
        'linux-x86_64': 'linux',
        'windows': 'linux',
        'windows-x86_64': 'linux',
    }[host]


def build_name(host, arch):
    """Gets the release build name for an NDK host tag.

    The builds are named by a short identifier like "linux" or "win64".

    >>> build_name('darwin-x86_64', 'arm')
    'arm'

    >>> build_name('windows', 'x86')
    'win_x86'
    """
    if host == 'darwin-x86_64':
        return arch

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


def download_build(branch, host, arch, build_number, download_dir):
    """Download a build from the build server."""
    url_base = 'https://android-build-uber.corp.google.com'
    path = 'builds/{branch}-{build_host}-{build_name}/{build_num}'.format(
        branch=branch,
        build_host=host_to_build_host(host),
        build_name=build_name(host, arch),
        build_num=build_number)

    pkg_name = package_name(host, arch)
    url = '{}/{}/{}'.format(url_base, path, pkg_name)

    timeout = '60'  # In seconds.
    out_file_path = os.path.join(download_dir, pkg_name)
    with open(out_file_path, 'w') as out_file:
        print('Downloading {} to {}'.format(url, out_file_path))
        subprocess.check_call(
            ['sso_client', '--location', '--request_timeout', timeout, url],
            stdout=out_file)
    return host, arch, out_file_path


def extract_package(package, host, install_dir):
    """Extract the downloaded toolchain."""
    host_dir = os.path.join(install_dir, 'toolchains', host)
    if not os.path.exists(host_dir):
        os.makedirs(host_dir)

    cmd = ['tar', 'xf', package, '-C', host_dir]
    subprocess.check_call(cmd)


def main():
    """Program entry point."""
    args = parse_args()

    os.chdir(os.path.realpath(os.path.dirname(__file__)))

    if not args.use_current_branch:
        subprocess.check_call(
            ['repo', 'start', 'update-gcc-{}'.format(args.build), '.'])

    download_dir = '.download'
    if os.path.isdir(download_dir):
        shutil.rmtree(download_dir)
    os.makedirs(download_dir)

    hosts = ('darwin-x86_64', 'linux-x86_64', 'windows', 'windows-x86_64')
    packages = []
    for host in hosts:
        for arch in build_support.ALL_ARCHITECTURES:
            package = download_build(
                args.branch, host, arch, args.build, download_dir)
            packages.append(package)

    install_dir = 'current'
    install_subdir = os.path.join(install_dir, 'toolchains')

    for host, arch, package in packages:
        toolchain = build_support.arch_to_toolchain(arch) + '-4.9'
        toolchain_path = os.path.join(install_subdir, host, toolchain)
        if os.path.exists(toolchain_path):
            print('Removing old {} {}...'.format(host, toolchain))
            subprocess.check_call(
                ['git', 'rm', '-rf', '--ignore-unmatch', toolchain_path])

            # Git doesn't believe in directories, so `git rm -rf` might leave
            # behind empty directories.
            if os.path.isdir(toolchain_path):
                shutil.rmtree(toolchain_path)

        if not os.path.exists(install_subdir):
            os.makedirs(install_subdir)

        print('Extracting {}...'.format(package))
        extract_package(package, host, install_dir)

        print('Adding {} {} files to index...'.format(host, toolchain))
        subprocess.check_call(['git', 'add', toolchain_path])

    print('Committing update...')
    message = 'Update prebuilt GCC to build {}.'.format(args.build)
    subprocess.check_call(['git', 'commit', '-m', message])

    shutil.rmtree(download_dir)


if __name__ == '__main__':
    main()
