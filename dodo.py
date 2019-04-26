import boto3
import dateutil.parser


def task_build_web_ami():
    return {
        'actions': [
            'packer validate packer/web.json',
            'packer build packer/web.json'
        ]
    }

def get_latest_ami(name, tags={}):
    client = boto3.client('ec2')
    response = client.describe_images(
        Filters=[
            {'Name': 'tag:{0}'.format(tag), 'Values': [value]}
            for tag, value in tags.items()])

    images = response['Images']
    if not images:
        raise RuntimeError(
            "no images with name prefix '{0}' and tags: {1}"
            "".format(name, tags))

    images.sort(key=lambda i: dateutil.parser.parse(i['CreationDate']))
    latest_image = images[-1]

    return {'ami': latest_image['ImageId']}

def task_detect_web_ami():
    image_tags = {'Project': 'Frontdesk'}

    return {
        'actions': [
            (get_latest_ami, ['frontdesk-web-'], {'tags': image_tags})
        ]
    }

def update_ssm_parameter(name, type, value):
    client = boto3.client('ssm')
    client.put_parameter(Name=name, Type=type, Value=value, Overwrite=True)

def task_update_web_ami():
    return {
        'actions': [
            (update_ssm_parameter, ['/Frontdesk/WebImageId', 'String'])
        ],
        'getargs': {
            'value': ('detect_web_ami', 'ami')
        }
    }
