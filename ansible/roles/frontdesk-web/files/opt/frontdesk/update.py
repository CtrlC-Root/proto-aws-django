#!/usr/bin/env python3

import os
import sys
import argparse
import traceback
import subprocess
from functools import reduce

import boto3
import requests


METADATA_URL = 'http://169.254.169.254/latest/meta-data'
STACK_ASG = 'WebAutoScalingGroup'
STACK_DBI = 'DatabaseInstance'
SYSTEMD_ENV_FILE = '/etc/default/frontdesk'
SYSTEMD_SERVICE = 'frontdesk-web'


def get_region():
    response = requests.get('{0}/placement/availability-zone'.format(METADATA_URL))
    return response.text[:-1]


def get_instance_id():
    response = requests.get('{0}/instance-id'.format(METADATA_URL))
    return response.text


def configure_service(name, run_and_enable):
    systemctl = '/bin/systemctl'
    unit = '{0}.service'.format(name)

    if run_and_enable:
        subprocess.run([systemctl, 'start', unit], check=True)
        subprocess.run([systemctl, 'enable', unit], check=True)

    else:
        subprocess.run([systemctl, 'stop', unit], check=True)
        subprocess.run([systemctl, 'disable', unit], check=True)


def get_instance_tags(session, instance_id):
    ec2 = session.resource('ec2')
    instance = ec2.Instance(instance_id)
    return {tag['Key']: tag['Value'] for tag in instance.tags}


def get_stack_outputs(session, stack_name):
    cloudformation = session.resource('cloudformation')
    stack = cloudformation.Stack(stack_name)
    return {i['OutputKey']: i['OutputValue'] for i in stack.outputs}


def get_stack_resource_id(session, stack_name, logical_id):
    cloudformation = session.client('cloudformation')
    response = cloudformation.describe_stack_resource(
        StackName=stack_name,
        LogicalResourceId=logical_id)

    return response['StackResourceDetail']['PhysicalResourceId']


def get_ssm_parameter(session, parameter_name):
    client = session.client('ssm')
    response = client.get_parameter(
        Name='/Frontdesk/{0}'.format(parameter_name),
        WithDecryption=True)

    return response['Parameter']['Value']


def signal_stack_asg(session, stack_name, asg_resource_name, success):
    client = session.client('cloudformation')
    client.signal_resource(
        StackName=stack_name,
        LogicalResourceId=asg_resource_name,
        UniqueId=get_instance_id(),
        Status=('SUCCESS' if success else 'FAILURE'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--signal-asg', action='store_true')

    args = parser.parse_args()

    # create the shared boto session
    session = boto3.session.Session(region_name=get_region())

    # retrieve the local instance tags
    tags = get_instance_tags(session, get_instance_id())
    stack_name = tags['aws:cloudformation:stack-name']

    # stop running services
    configure_service(SYSTEMD_SERVICE, False)

    try:
        # locate the deployment bucket
        outputs = get_stack_outputs(session, stack_name)

        s3 = session.resource('s3')
        bucket = s3.Bucket(outputs['DeploymentBucket'])

        # download the application
        filename = get_ssm_parameter(session, 'ApplicationBuild')
        object = bucket.Object(filename)

        # download the application
        application = reduce(
            os.path.join,
            [os.path.sep, 'opt', 'frontdesk', 'app', filename])

        object.download_file(application)
        os.chmod(application, 0o755)

        # retrieve the database settings
        rds = session.client('rds')
        dbinstance_id = get_stack_resource_id(session, stack_name, STACK_DBI)
        response = rds.describe_db_instances(
            DBInstanceIdentifier=dbinstance_id)

        instance_data = response['DBInstances'][0]
        db_name = instance_data['DBName']
        db_user = instance_data['MasterUsername']
        db_pass = get_ssm_parameter(session, 'DatabaseMasterPassword')
        db_host = instance_data['Endpoint']['Address']
        db_port = instance_data['Endpoint']['Port']

        # write the environment file
        env_vars = {
            'FRONTDESK_APP': application,
            'SECRET_KEY': get_ssm_parameter(session, 'SecretKey'),
            'DB_NAME': db_name,
            'DB_USER': db_user,
            'DB_PASS': db_pass,
            'DB_HOST': db_host,
            'DB_PORT': str(db_port)}

        with open(SYSTEMD_ENV_FILE, 'w') as env_file:
            for key, value in env_vars.items():
                env_file.write('{0}="{1}"\n'.format(key, value))

        # export environment variables
        for key, value in env_vars.items():
            os.environ[key] = value

        # run database migrations
        subprocess.run([application, 'migrate'], check=True)

        # production checks
        subprocess.run([application, 'check', '--deploy'], check=True)

        # enable and start the service
        configure_service(SYSTEMD_SERVICE, True)

    except Exception as e:
        if args.signal_asg:
            print("Sending failure signal to ASG")
            signal_stack_asg(session, stack_name, STACK_ASG, False)

        traceback.print_exc()
        sys.exit(1)

    if args.signal_asg:
        print("Sending success signal to ASG")
        signal_stack_asg(session, stack_name, STACK_ASG, True)


if __name__ == '__main__':
    main()
