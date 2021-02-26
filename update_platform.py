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
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap
from typing import Dict, Iterable, Sequence, Tuple


THIS_DIR = Path(__file__).resolve().parent


def logger() -> logging.Logger:
    """Returns the module logger."""
    return logging.getLogger(__name__)


def check_call(cmd: Sequence[str]) -> None:
    """subprocess.check_call with logging."""
    logger().debug('check_call `%s`', ' '.join(cmd))
    subprocess.check_call(cmd)


def rmtree(path: Path) -> None:
    """shutil.rmtree with logging."""
    logger().debug('rmtree %s', path)
    shutil.rmtree(str(path))


def makedirs(path: Path) -> None:
    """os.makedirs with logging."""
    logger().debug('mkdir -p %s', path)
    path.mkdir(parents=True, exist_ok=True)


def remove(path: Path) -> None:
    """os.remove with logging."""
    logger().debug('rm %s', path)
    path.unlink()


def rename(src: Path, dst: Path) -> None:
    """os.rename with logging."""
    logger().debug('mv %s %s', src, dst)
    src.rename(dst)


def fetch_artifact(branch: str, target: str, build: str, pattern: str) -> None:
    """Fetches an artifact from the build server."""
    fetch_artifact_path = '/google/data/ro/projects/android/fetch_artifact'
    cmd = [
        fetch_artifact_path, '--branch', branch, '--target=' + target, '--bid',
        build, pattern
    ]
    check_call(cmd)


def remove_unwanted_platforms(install_path: Path,
                              remove_platforms: Iterable[str]) -> None:
    """Removes platforms that should not be checked in."""
    for platform in remove_platforms:
        platform_path = install_path / f'platforms/android-{platform}'
        if platform_path.exists():
            rmtree(platform_path)

    # The android-current platform is actually the future platform version (not
    # even assigned to a codename), which should not be included in the NDK.
    current_platform = install_path / 'platforms/android-current'
    rmtree(current_platform)

    rel_platform = install_path / 'platforms/android-REL'
    if rel_platform.exists():
        rmtree(rel_platform)


def rename_codenamed_releases(install_path: Path,
                              rename_codenames: Dict[str, str]) -> None:
    """Rename codenamed releases."""
    for codename, new_name in rename_codenames.items():
        codename_path = install_path / f'platforms/android-{codename}'
        new_name_path = install_path / f'platforms/android-{new_name}'

        if new_name_path.exists():
            raise RuntimeError(
                f'Could not rename android-{codename} to android-{new_name} '
                f'because android-{new_name} already exists.')

        rename(codename_path, new_name_path)


def verify_no_codenames(install_path: Path) -> None:
    """Checks for codenamed releases and raises an error if any are found."""
    codenames = set()
    for release in install_path.glob('platforms/android-*'):
        name = release.name
        _, version = name.split('-', maxsplit=1)
        try:
            int(version)
        except ValueError:
            codenames.add(release)
    if codenames:
        codename_lines = '\n'.join(str(c) for c in codenames)
        sys.exit(
            'Found unhandled codenamed releases in the sysroot. Clang '
            'requires numeric releases, so codenamed releases must either be '
            'removed using --remove-platform or renamed using '
            f'--rename-codename. Found codenames:\n{codename_lines}')


def in_pore_tree() -> bool:
    """Returns True if the tree is using pore instead of repo."""
    top = THIS_DIR.parent.parent
    return (top / '.pore').exists()


def pore_path() -> Path:
    """Returns the command to run for repo."""
    pore = shutil.which('pore')
    if pore is None:
        raise RuntimeError('Could not find pore in PATH.')
    return Path(pore)


def start_branch(name: str) -> None:
    """Starts a branch in the project."""
    pore = in_pore_tree()
    if pore:
        args = [str(pore_path())]
    else:
        args = ['repo']
    args.extend(['start', name])
    if not pore:
        args.append('.')
    check_call(args)


def kv_arg_pair(arg: str) -> Tuple[str, str]:
    """Parses a key/value argument pair."""
    error_msg = 'Argument must be in format key=value, got ' + arg
    try:
        key, value = arg.split('=')
    except ValueError:
        raise argparse.ArgumentTypeError(error_msg)

    if key == '' or value == '':
        raise argparse.ArgumentTypeError(error_msg)

    return key, value


def parse_args() -> argparse.Namespace:
    """Parses and returns command line arguments."""
    parser = argparse.ArgumentParser()

    download_group = parser.add_mutually_exclusive_group()

    download_group.add_argument(
        '--download',
        action='store_true',
        default=True,
        help='Fetch artifacts from the build server. BUILD is a build number.')

    download_group.add_argument(
        '--no-download',
        action='store_false',
        dest='download',
        help=('Do not download build artifacts. BUILD points to a local '
              'artifact.'))

    parser.add_argument(
        'build',
        metavar='BUILD_OR_ARTIFACT',
        help=('Build number to pull from the build server, or a path to a '
              'local artifact'))

    parser.add_argument('--branch',
                        default='aosp-master',
                        help='Branch to pull from the build server.')

    parser.add_argument('-b',
                        '--bug',
                        default='None',
                        help='Bug URL for commit message.')

    parser.add_argument('--use-current-branch',
                        action='store_true',
                        help='Do not repo start a new branch for the update.')

    parser.add_argument('--remove-platform',
                        action='append',
                        default=[],
                        help='Remove platforms directories.')

    parser.add_argument(
        '--rename-codename',
        action='append',
        type=kv_arg_pair,
        default=[],
        help='Rename codename platform. Example: --rename-codename O=26.')

    return parser.parse_args()


def main() -> None:
    """Program entry point."""
    logging.basicConfig(level=logging.DEBUG)

    args = parse_args()

    if args.download:
        build = args.build
        branch_name_suffix = build
    else:
        package = Path(args.build)
        branch_name_suffix = 'local'
        logger().info('Using local artifact at %s', package)

    os.chdir(os.path.realpath(os.path.dirname(__file__)))

    if not args.use_current_branch:
        start_branch(f'update-platform-{branch_name_suffix}')

    install_path = Path('platform')
    check_call(['git', 'rm', '-r', '--ignore-unmatch', str(install_path)])
    if install_path.exists():
        rmtree(install_path)
    makedirs(install_path)

    if args.download:
        fetch_artifact(args.branch, 'ndk', build, 'ndk_platform.tar.bz2')
        package = Path('ndk_platform.tar.bz2')

    check_call([
        'tar', 'xf', str(package), '--strip-components=1', '-C',
        str(install_path)
    ])

    if args.download:
        remove(package)

    # It's easier to rearrange the package here than it is in the NDK's build.
    # NOTICE is in the package root by convention, but we don't actually want
    # this whole package to be the installed sysroot in the NDK.  We have
    # $INSTALL_DIR/sysroot and $INSTALL_DIR/platforms. $INSTALL_DIR/sysroot
    # will be installed to $NDK/sysroot, but $INSTALL_DIR/platforms is used as
    # input to Platforms. Shift the NOTICE into the sysroot directory.
    rename(install_path / 'NOTICE', install_path / 'sysroot/NOTICE')

    remove_unwanted_platforms(install_path, args.remove_platform)
    rename_codenamed_releases(install_path, dict(args.rename_codename))
    verify_no_codenames(install_path)

    check_call(['git', 'add', str(install_path)])

    if args.download:
        update_msg = f'to build {build}'
    else:
        update_msg = 'with local artifact'

    message = textwrap.dedent(f"""\
        Update NDK platform prebuilts {update_msg}.

        Test: ndk/checkbuild.py && ndk/run_tests.py
        Bug: {args.bug}
        """)
    check_call(['git', 'commit', '-m', message])


if __name__ == '__main__':
    main()
