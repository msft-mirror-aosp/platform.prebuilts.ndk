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
"""Update the NDK platform prebuilts from the build server."""
import argparse
import logging
import os
import textwrap


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


def rename(src, dst):
    """os.rename with logging."""
    logger().debug('mv %s %s', src, dst)
    os.rename(src, dst)


def fetch_artifact(branch, target, build, pattern):
    """Fetches an artifact from the build server."""
    fetch_artifact_path = '/google/data/ro/projects/android/fetch_artifact'
    cmd = [fetch_artifact_path, '--branch', branch, '--target=' + target,
           '--bid', build, pattern]
    check_call(cmd)


def fetch_ndk_prebuilts(branch, build):
    """Fetches a NDK platform package."""
    target = 'ndk'
    fetch_artifact(branch, target, build, 'ndk_platform.tar.bz2')


def parse_args():
    """Parses and returns command line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'build', metavar='BUILD',
        help='Build number to pull from the build server.')

    parser.add_argument(
        '--branch', default='aosp-master',
        help='Branch to pull from the build server.')

    parser.add_argument(
        '-b', '--bug', default='None', help='Bug URL for commit message.')

    parser.add_argument(
        '--use-current-branch', action='store_true',
        help='Do not repo start a new branch for the update.')

    return parser.parse_args()


def main():
    """Program entry point."""
    logging.basicConfig(level=logging.DEBUG)

    args = parse_args()

    os.chdir(os.path.realpath(os.path.dirname(__file__)))

    if not args.use_current_branch:
        check_call(
            ['repo', 'start', 'update-platform-{}'.format(args.build), '.'])

    install_path = 'platform'
    check_call(['git', 'rm', '-r', '--ignore-unmatch', install_path])
    if os.path.exists(install_path):
        rmtree(install_path)
    makedirs(install_path)

    fetch_ndk_prebuilts(args.branch, args.build)
    package = 'ndk_platform.tar.bz2'
    check_call(['tar', 'xf', package, '--strip-components=1', '-C',
                install_path])
    remove(package)

    fetch_artifact(args.branch, 'ndk', args.build, 'repo.prop')
    rename('repo.prop', os.path.join(install_path, 'repo.prop'))

    check_call(['git', 'add', install_path])
    message = textwrap.dedent("""\
        Update NDK platform prebuilts to build {}.

        Test: ndk/checkbuild.py && ndk/validate.py
        Bug: {}
        """.format(args.build, args.bug))
    check_call(['git', 'commit', '-m', message])

    # Fetch artifact dumps crap to the working directory.
    remove('.fetch_artifact2.dat')


if __name__ == '__main__':
    main()
