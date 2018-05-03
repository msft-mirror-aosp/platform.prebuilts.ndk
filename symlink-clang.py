#!/usr/bin/env python
#
# Copyright (C) 2016 The Android Open Source Project
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
"""Update symlinks to our prebuilt clang.

While GCC is actually installed here because we need a different set of GCCs
than the platform (a superset because the NDK doesn't know how to deal with
multilib toolchains), we can just symlink clang.
"""
from __future__ import print_function

import argparse
import functools
import os
import re
import site
import subprocess

site.addsitedir(os.path.join(os.path.dirname(__file__), '../../ndk/build/lib'))

import build_support  # pylint: disable=import-error


@functools.total_ordering
class ClangVersion(object):
    def __init__(self, revision, patch):
        self.revision = revision
        self.patch = patch

    @staticmethod
    def from_dirname(dirname):
        if not dirname.startswith('clang-r'):
            raise ValueError

        _, _, name = dirname.partition('clang-r')

        pattern = r'^(\d+)([a-z]?)$'
        match = re.match(pattern, name)
        if not match:
            raise ValueError('Expected clang name to match {}'.format(pattern))

        revision = int(match.group(1))
        patch = match.group(2)
        return ClangVersion(revision, patch)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return 'r{}{}'.format(self.revision, self.patch)

    def as_tuple(self):
        return (self.revision, self.patch)

    def __eq__(self, other):
        return self.as_tuple() == other.as_tuple()

    def __lt__(self, other):
        return self.as_tuple() < other.as_tuple()


def get_latest_build():
    dirs = os.listdir(build_support.android_path(
        'prebuilts/clang/host/linux-x86'))

    clangs = []
    for dir_name in dirs:
        if not dir_name.startswith('clang-r'):
            continue
        clangs.append(ClangVersion.from_dirname(dir_name))
    return str(sorted(clangs)[-1])


def get_prebuilt_host(host):
    """Maps from an NDK host tag to a platform host tag."""
    return {
        'darwin-x86_64': 'darwin-x86',
        'linux-x86_64': 'linux-x86',
        'windows': 'windows-x86_32',
        'windows-x86_64': 'windows-x86',
    }[host]


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'build', metavar='BUILD', nargs='?',
        help='Build number to symlink. Defaults to the latest available.')

    parser.add_argument(
        '--use-current-branch', action='store_true',
        help='Do not repo start a new branch for the update.')

    return parser.parse_args()


def main():
    args = parse_args()

    os.chdir(os.path.realpath(os.path.dirname(__file__)))

    build = args.build
    if build is None:
        build = get_latest_build()

    if not args.use_current_branch:
        subprocess.check_call(
            ['repo', 'start', 'update-clang-{}'.format(build), '.'])

    hosts = ('darwin-x86_64', 'linux-x86_64', 'windows', 'windows-x86_64')
    for host in hosts:
        install_path = build_support.android_path(
            'prebuilts/ndk/current/toolchains', host, 'llvm')
        if os.path.lexists(install_path):
            print('Removing old Clang link for {}...'.format(host))
            subprocess.check_call(['git', 'rm', install_path])

        prebuilt_host = get_prebuilt_host(host)
        prebuilt_path = build_support.android_path(
            'prebuilts/clang/host', prebuilt_host, 'clang-{}'.format(build))

        install_dir = os.path.dirname(install_path)
        relative_path = os.path.relpath(prebuilt_path, install_dir)

        print(relative_path, install_path)
        print('Linking {} clang-{}...'.format(host, build))
        os.symlink(relative_path, install_path)

        print('Adding {} link to index...'.format(host))
        subprocess.check_call(['git', 'add', install_path])

    print('Committing update...')
    message = 'Update prebuilt Clang to build {}.'.format(build)
    subprocess.check_call(['git', 'commit', '-m', message])


if __name__ == '__main__':
    main()
