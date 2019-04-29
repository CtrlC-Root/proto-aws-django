import os
from itertools import chain

from multitool import (
    find_files,
    find_latest_ami,
    update_ssm_parameter)


def task_build_web_ami():
    return {
        'file_dep': list(chain(
            find_files('packer'),
            find_files('scripts'))),
        'actions': [
            'packer validate packer/web.json',
            'packer build packer/web.json'
        ]
    }


def task_detect_web_ami():
    name_prefix = 'frontdesk-web-'
    tags = {'Project': 'Frontdesk'}

    return {
        'actions': [
            (find_latest_ami, [name_prefix], {'tags': tags})
        ]
    }


def task_update_web_ami():
    return {
        'actions': [
            (update_ssm_parameter, ['/Frontdesk/WebImageId', 'String'])
        ],
        'getargs': {
            'value': ('detect_web_ami', 'ami')
        }
    }


def task_build_frontdesk_pex():
    package_root = os.path.join(os.getcwd(), 'pkg/frontdesk')
    requirements_file = os.path.join(package_root, 'requirements.txt')
    pex_file = os.path.join(package_root, 'frontdesk-0.1.pex')

    return {
        'file_dep': find_files(
            package_root,
            include=['*.py', '*.html'],
            extra=['requirements.txt', 'MANIFEST.in']
        ),
        'actions': [
            [
                'pex',
                '-v', package_root,
                '-r', requirements_file,
                '--disable-cache',
                '-c', 'frontdesk',
                '-o', pex_file
            ],
        ],
        'targets': [
            pex_file
        ],
        'clean': True
    }
