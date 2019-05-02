#!/usr/bin/env python

import os
import sys
import argparse
import subprocess
import configparser


def detect_build_name(project_path):
    setup_path = os.path.join(project_path, 'setup.py')
    name_command = subprocess.run(
        ['python', setup_path, '--name'],
        check=True,
        stdout=subprocess.PIPE)

    return name_command.stdout.decode().strip()


def detect_build_version(project_path):
    setup_path = os.path.join(project_path, 'setup.py')
    version_command = subprocess.run(
        ['python', setup_path, '--version'],
        check=True,
        stdout=subprocess.PIPE)

    return version_command.stdout.decode().strip()


def detect_entry_points(project_path):
    setup_path = os.path.join(project_path, 'setup.py')
    egg_command = subprocess.run(
        ['python', setup_path, 'egg_info'],
        check=True,
        stdout=subprocess.PIPE)

    output_lines = egg_command.stdout.decode().strip().split('\n')
    entry_lines = list(filter(
        lambda l: l.startswith('writing entry points to'),
        output_lines))

    entry_points_file = os.path.join(
        project_path,
        entry_lines[0].split(' ')[-1])

    config = configparser.ConfigParser()
    config.read(entry_points_file)
    return list(config['console_scripts'])


def create_build(project_path, output_path):
    # detect build name and version
    build_name = detect_build_name(project_path)
    build_version = detect_build_version(project_path)

    # detect the entry point
    scripts = detect_entry_points(project_path)
    entry_point = scripts[0]

    # locate project requirements
    requirements_file = os.path.join(project_path, 'requirements.txt')

    # determine the output path
    pex_file = os.path.join(
        output_path,
        '{0}-{1}.pex'.format(build_name, build_version))

    # output build settings
    print("Name:", build_name)
    print("Version:", build_version)
    print("Entry Point:", entry_point)
    print("Requirements:", requirements_file)
    print("Build:", pex_file)

    # create the pex file
    subprocess.run([
        'pex',
        '-v', project_path,
        '-r', requirements_file,
        '--disable-cache',
        '-c', entry_point,
        '-o', pex_file
    ], check=True)


if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--project-path', '-p',
        required=True,
        help='project path (contains setup.py)')

    parser.add_argument(
        '--output-path', '-o',
        default=os.getcwd(),
        help='build output path (will contain PEX file)')

    args = parser.parse_args()

    # create the build
    create_build(args.project_path, args.output_path)
