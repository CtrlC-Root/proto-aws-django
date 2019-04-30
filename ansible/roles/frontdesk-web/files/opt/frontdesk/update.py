#!/usr/bin/env python3

import os
import traceback
import subprocess
from functools import reduce

import boto3
import requests


METADATA_URL = 'http://169.254.169.254/latest/meta-data'
STACK_ASG = 'WebAutoScalingGroup'
SYSTEMD_ENV_FILE = '/etc/default/frontdesk'
SYSTEMD_SERVICE = 'frontdesk-web'


def get_region():
    response = requests.get('{0}/placement/availability-zone'.format(METADATA_URL))
    return response.text[:-1]


def get_instance_id():
    response = requests.get('{0}/instance-id'.format(METADATA_URL))
    return response.text


def get_instance_tags(session, instance_id):
    ec2 = session.resource('ec2')
    instance = ec2.Instance(instance_id)
    return {tag['Key']: tag['Value'] for tag in instance.tags}


def get_stack_outputs(session, stack_name):
    cloudformation = session.resource('cloudformation')
    stack = cloudformation.Stack(stack_name)
    return {i['OutputKey']: i['OutputValue'] for i in stack.outputs}


def get_ssm_parameter(session, parameter_name):
    client = session.client('ssm')
    response = client.get_parameter(Name=parameter_name, WithDecryption=True)
    return response['Parameter']['Value']


def signal_stack_asg(session, stack_name, asg_resource_name, success):
    client = session.client('cloudformation')
    client.signal_resource(
        StackName=stack_name,
        LogicalResourceId=asg_resource_name,
        UniqueId=get_instance_id(),
        Status=('SUCCESS' if success else 'FAILURE'))


def main():
    # create the shared boto session
    session = boto3.session.Session(region_name=get_region())

    # retrieve the local instance tags
    tags = get_instance_tags(session, get_instance_id())
    stack_name = tags['aws:cloudformation:stack-name']

    try:
        # locate the deployment bucket
        outputs = get_stack_outputs(session, stack_name)

        s3 = session.resource('s3')
        bucket = s3.Bucket(outputs['DeploymentBucket'])

        # download the application
        filename = get_ssm_parameter(session, '/Frontdesk/ApplicationBuild')
        object = bucket.Object(filename)

        # download the application
        application = reduce(
            os.path.join,
            [os.path.sep, 'opt', 'frontdesk', 'app', filename])

        object.download_file(application)
        os.chmod(application, 0o755)

        # write the environment file
        with open(SYSTEMD_ENV_FILE, 'w') as env_file:
            env_file.write('FRONTDESK_APP="{0}"\n'.format(application))

        # enable and start the service
        service = '{0}.service'.format(SYSTEMD_SERVICE)
        subprocess.run(['/bin/systemctl', 'enable', service], check=True)
        subprocess.run(['/bin/systemctl', 'start', service], check=True)

    except Exception as e:
        print("Sending failure signal to ASG")
        signal_stack_asg(session, stack_name, STACK_ASG, False)

        traceback.print_exc()

    else:
        print("Sending success signal to ASG")
        signal_stack_asg(session, stack_name, STACK_ASG, True)


if __name__ == '__main__':
    main()
