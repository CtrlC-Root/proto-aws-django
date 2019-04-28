import boto3
import dateutil.parser


def find_latest_ami(name, tags={}):
    """
    Retrieve the latest EC2 AMI by creation date that matches the given name
    prefix and tags.
    """

    client = boto3.client('ec2')
    response = client.describe_images(
        Filters=[
            {'Name': 'tag:{0}'.format(tag), 'Values': [value]}
            for tag, value in tags.items()])

    images = response['Images']
    if not images:
        raise RuntimeError(
            "no ec2 images with name prefix '{0}' and tags: {1}"
            "".format(name, tags))

    images.sort(key=lambda i: dateutil.parser.parse(i['CreationDate']))
    latest_image = images[-1]

    return {'ami': latest_image['ImageId']}
