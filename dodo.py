import os

from multitool import (
    find_files,
    find_latest_ami,
    update_ssm_parameter)


def task_build_web_ami():
    return {
        'file_dep': find_files('packer'),
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
