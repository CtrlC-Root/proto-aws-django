#!/usr/bin/env python

import os
import sys
import time
import argparse

import boto3
import fabric

STACK_NAME = 'Frontdesk'
STACK_ASG = 'WebAutoScalingGroup'
BUILD_PARAMETER = '/Frontdesk/ApplicationBuild'
ASG_PROCESSES = [
    'HealthCheck',
    'ReplaceUnhealthy',
    'AZRebalance',
    'ScheduledActions',
    'AlarmNotification']


def main():
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--app-build', '-a',
        required=True,
        help='application build')

    args = parser.parse_args()

    # retrieve the stack and it's outputs
    cloudformation = boto3.resource('cloudformation')
    stack = cloudformation.Stack(STACK_NAME)
    outputs = {i['OutputKey']: i['OutputValue'] for i in stack.outputs}

    # determine the deployment bucket
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(outputs['DeploymentBucket'])

    # upload the application build
    print("Uploading {0} to {1}".format(args.app_build, bucket.name))
    application = os.path.basename(args.app_build)
    bucket.upload_file(args.app_build, application)

    # retrieve autoscaling group
    asg = stack.Resource(STACK_ASG)
    asg_name = asg.physical_resource_id

    # suspend autoscaling processes
    print("Suspend {0} processes".format(asg_name))
    autoscaling = boto3.client('autoscaling')
    autoscaling.suspend_processes(
        AutoScalingGroupName=asg_name,
        ScalingProcesses=ASG_PROCESSES)

    # retrieve instances in autoscaling group
    response = autoscaling.describe_auto_scaling_groups(
        AutoScalingGroupNames=[asg_name])

    ec2 = boto3.resource('ec2')
    instance_data = response['AutoScalingGroups'][0]['Instances']
    instances = [ec2.Instance(d['InstanceId']) for d in instance_data]

    # update the build parameter
    print("Set '{0}' to '{1}'".format(BUILD_PARAMETER, application))
    ssm = boto3.client('ssm')
    ssm.put_parameter(
        Name=BUILD_PARAMETER,
        Type='String',
        Value=application,
        Overwrite=True)

    # update instances sequentially
    for instance in instances:
        # standby the instance
        print("Moving instance {0} to standby".format(instance.id))
        autoscaling.enter_standby(
            AutoScalingGroupName=asg_name,
            InstanceIds=[instance.id],
            ShouldDecrementDesiredCapacity=True)

        print("Waiting...", end='')
        sys.stdout.flush()
        time.sleep(3)

        while True:
            response = autoscaling.describe_auto_scaling_instances(
                InstanceIds=[instance.id])

            state = response['AutoScalingInstances'][0]['LifecycleState']
            if state == 'Standby':
                print("OK")
                break

            elif state != 'EnteringStandby':
                print("FAILED\n{0}".format(state))
                sys.exit(1)

            print(".", end='')
            sys.stdout.flush()
            time.sleep(1)

        # connect to the instance and run the update script
        print("Updating instance...")
        connection = fabric.Connection(instance.public_ip_address, user='ubuntu')
        result = connection.run('sudo -H python3 /opt/frontdesk/update.py')

        # resume the instance
        print("Moving instance {0} to service pool".format(instance.id))
        autoscaling.exit_standby(
            AutoScalingGroupName=asg_name,
            InstanceIds=[instance.id])

        print("Waiting...", end='')
        sys.stdout.flush()
        time.sleep(3)

        while True:
            response = autoscaling.describe_auto_scaling_instances(
                InstanceIds=[instance.id])

            state = response['AutoScalingInstances'][0]['LifecycleState']
            if state == 'InService':
                print("OK")
                break

            elif state != 'Pending':
                print("FAILED\n{0}".format(state))
                sys.exit(1)

            print(".", end='')
            sys.stdout.flush()
            time.sleep(1)

    # resume autoscaling processes
    print("Resume {0} processes".format(asg_name))
    autoscaling.resume_processes(AutoScalingGroupName=asg_name)


if __name__ == '__main__':
    main()
