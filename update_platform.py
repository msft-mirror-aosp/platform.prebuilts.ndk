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


def remove_unwanted_platforms(install_path, remove_platforms):
    """Removes platforms that should not be checked in."""
    for platform in remove_platforms:
        platform_path = os.path.join(
            install_path, 'platforms/android-{}'.format(platform))
        if os.path.exists(platform_path):
            rmtree(platform_path)

    # The android-current platform is actually the future platform version (not
    # even assigned to a codename), which should not be included in the NDK.
    current_platform = os.path.join(install_path, 'platforms/android-current')
    rmtree(current_platform)

    rel_platform = os.path.join(install_path, 'platforms/android-REL')
    if os.path.exists(rel_platform):
        rmtree(rel_platform)


def rename_codenamed_releases(install_path, rename_codenames):
    """Rename codenamed releases."""
    for codename, new_name in rename_codenames:
        codename_path = os.path.join(
            install_path, 'platforms/android-' + codename)
        new_name_path = os.path.join(
            install_path, 'platforms/android-' + new_name)

        if os.path.exists(new_name_path):
            raise RuntimeError(
                'Could not rename android-{0} to android-{1} because '
                'android-{1} already exists.'.format(codename, new_name))

        rename(codename_path, new_name_path)


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
        '--remove-platform', action='append', default=[],
        help='Remove platforms directories.')

    parser.add_argument(
        '--rename-codename', action='append', type=kv_arg_pair, default=[],
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
        logger().info('Using local artifact at %s', package)

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
        fetch_artifact(args.branch, 'ndk', build, 'ndk_platform.tar.bz2')
        package = 'ndk_platform.tar.bz2'

    check_call(['tar', 'xf', package, '--strip-components=1', '-C',
                install_path])

    if args.download:
        remove(package)

    # It's easier to rearrange the package here than it is in the NDK's build.
    # NOTICE is in the package root by convention, but we don't actually want
    # this whole package to be the installed sysroot in the NDK.  We have
    # $INSTALL_DIR/sysroot and $INSTALL_DIR/platforms. $INSTALL_DIR/sysroot
    # will be installed to $NDK/sysroot, but $INSTALL_DIR/platforms is used as
    # input to Platforms. Shift the NOTICE into the sysroot directory.
    rename(os.path.join(install_path, 'NOTICE'),
           os.path.join(install_path, 'sysroot/NOTICE'))

    remove_unwanted_platforms(install_path, args.remove_platform)
    rename_codenamed_releases(install_path, args.rename_codename)

    check_call(['git', 'add', install_path])

    if args.download:
        update_msg = 'to build {}'.format(build)
    else:
        update_msg = 'with local artifact'

    message = textwrap.dedent("""\
        Update NDK platform prebuilts {}.

        Test: ndk/checkbuild.py && ndk/run_tests.py
        Bug: {}
        """.format(update_msg, args.bug))
    check_call(['git', 'commit', '-m', message])


if __name__ == '__main__':
    main()
