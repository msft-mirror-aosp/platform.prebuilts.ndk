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

    # Fetch artifact dumps crap to the working directory.
    remove('.fetch_artifact2.dat')


def fetch_ndk_prebuilts(branch, build):
    """Fetches a NDK platform package."""
    target = 'ndk'
    fetch_artifact(branch, target, build, 'ndk_platform.tar.bz2')
    fetch_artifact(branch, target, build, 'repo.prop')


def kv_arg_pair(arg):
    """Parses a key/value argument pair."""
    error_msg = 'Argument must be in format key=value, got ' + arg
    try:
        key, value = arg.split('=')
    except ValueError:
        raise argparse.ArgumentTypeError(error_msg)

    if key == '' or value == '':
        raise argparse.ArgumentTypeError(error_msg)

    return key, value


def parse_args():
    """Parses and returns command line arguments."""
    parser = argparse.ArgumentParser()

    download_group = parser.add_mutually_exclusive_group()

    download_group.add_argument(
        '--download', action='store_true', default=True,
        help='Fetch artifacts from the build server. BUILD is a build number.')

    download_group.add_argument(
        '--no-download', action='store_false', dest='download',
        help=('Do not download build artifacts. BUILD points to a local '
              'artifact.'))

    parser.add_argument(
        'build', metavar='BUILD_OR_ARTIFACT',
        help=('Build number to pull from the build server, or a path to a '
              'local artifact'))

    parser.add_argument(
        '--branch', default='aosp-master',
        help='Branch to pull from the build server.')

    parser.add_argument(
        '-b', '--bug', default='None', help='Bug URL for commit message.')

    parser.add_argument(
        '--use-current-branch', action='store_true',
        help='Do not repo start a new branch for the update.')

    parser.add_argument(
        '--include-current', metavar='CODENAME',
        help='Do not remove android-current. Rename as android-CODENAME.')

    parser.add_argument(
        '--rename-codename', action='append', type=kv_arg_pair,
        help='Rename codename platform. Example: --rename-codename O=26.')

    return parser.parse_args()


def main():
    """Program entry point."""
    logging.basicConfig(level=logging.DEBUG)

    args = parse_args()

    if args.download:
        build = args.build
        branch_name_suffix = build
    else:
        package = os.path.realpath(args.build)
        branch_name_suffix = 'local'
        logger().info('Using local artifact at {}'.format(package))

    os.chdir(os.path.realpath(os.path.dirname(__file__)))

    if not args.use_current_branch:
        branch_name = 'update-platform-' + branch_name_suffix
        check_call(['repo', 'start', branch_name, '.'])

    install_path = 'platform'
    check_call(['git', 'rm', '-r', '--ignore-unmatch', install_path])
    if os.path.exists(install_path):
        rmtree(install_path)
    makedirs(install_path)

    if args.download:
        fetch_ndk_prebuilts(args.branch, build)
        package = 'ndk_platform.tar.bz2'

    check_call(['tar', 'xf', package, '--strip-components=1', '-C',
                install_path])

    if args.download:
        remove(package)

    # It's easier to rearrange the package here than it is in the NDK's build.
    # NOTICE and repo.prop are in the package root by convention, but we don't
    # actually want this whole package to be the installed sysroot in the NDK.
    # We have $INSTALL_DIR/sysroot and $INSTALL_DIR/platforms.
    # $INSTALL_DIR/sysroot will be installed to $NDK/sysroot, but
    # $INSTALL_DIR/platforms is used as input to gen-platforms.sh. Shift the
    # repo.prop and NOTICE into the sysroot directory.
    if args.download:
        rename('repo.prop', os.path.join(install_path, 'sysroot/repo.prop'))
    rename(os.path.join(install_path, 'NOTICE'),
           os.path.join(install_path, 'sysroot/NOTICE'))

    # When we don't have preview releases or betas of the platform in progress,
    # we want to strip out unreleased API levels. During the preview/beta
    # cycles, we want to keep them and rename "current" to the expected
    # platform number.
    current_platform = os.path.join(install_path, 'platforms/android-current')
    if args.include_current is None:
        rmtree(current_platform)
    else:
        codename = 'android-' + args.include_current
        codename_platform = os.path.join(install_path, 'platforms', codename)
        rename(current_platform, codename_platform)

    for codename, new_name in args.rename_codename:
        codename_path = os.path.join(
            install_path, 'platforms/android-' + codename)
        new_name_path = os.path.join(
            install_path, 'platforms/android-' + new_name)

        if os.path.exists(new_name_path):
            raise RuntimeError(
                'Could not rename android-{0} to android-{1} because '
                'android-{1} already exists.'.format(codename, new_name))

        rename(codename_path, new_name_path)

    check_call(['git', 'add', install_path])

    if args.download:
        update_msg = 'to build {}'.format(build)
    else:
        update_msg = 'with local artifact'

    message = textwrap.dedent("""\
        Update NDK platform prebuilts {}.

        Test: ndk/checkbuild.py && ndk/validate.py
        Bug: {}
        """.format(update_msg, args.bug))
    check_call(['git', 'commit', '-m', message])


if __name__ == '__main__':
    main()
