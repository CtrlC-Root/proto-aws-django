#!/usr/bin/env python

import os
import sys
import time
import argparse

import boto3

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

    instance_data = response['AutoScalingGroups'][0]['Instances']
    instance_ids = [d['InstanceId'] for d in instance_data]

    # update the build parameter
    print("Set {0}: {1}".format(BUILD_PARAMETER, application))
    ssm = boto3.client('ssm')
    ssm.put_parameter(
        Name=BUILD_PARAMETER,
        Type='String',
        Value=application,
        Overwrite=True)

    # update instances sequentially
    for instance_id in instance_ids:
        # standby the instance
        print("Moving instance to standby: {0}".format(instance_id))
        autoscaling.enter_standby(
            AutoScalingGroupName=asg_name,
            InstanceIds=[instance_id],
            ShouldDecrementDesiredCapacity=False)

        print("Waiting...", end='')
        time.sleep(5)

        while True:
            response = autoscaling.describe_auto_scaling_instances(
                InstanceIds=[instance_id])

            state = response['AutoScalingInstances'][0]['LifecycleState']
            if state == 'Standby':
                print("OK")
                break

            elif state != 'EnteringStandby':
                print("FAILED\n{0}".format(state))
                sys.exit(1)

            print(".", end='')
            time.sleep(1)

        # run the update script on the instance
        print("Updating instance: {0}".format(instance_id))
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Comment='Update frontdesk web app',
            Parameters={'commands': ['/opt/frontdesk/update.py']})

        command_id = response['Command']['CommandId']

        # wait for command to finish running
        print("Waiting...", end='')
        time.sleep(5)

        while True:
            response = ssm.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id)

            status = response['Status']
            if status == 'Success':
                print("OK")
                break

            elif status in ['Cancelled', 'TimedOut', 'Failed']:
                print("FAILED\n{0}".format(response['StatusDetail']))
                sys.exit(1)

            print(".", end='')
            time.sleep(1)

        # resume the instance
        autoscaling.exit_standby(
            AutoScalingGroupName=asg_name,
            InstanceIds=[instance_id])

    # resume autoscaling processes
    print("Resume {0} processes".format(asg_name))
    autoscaling.resume_processes(
        AutoScalingGroupName=asg_name,
        ScalingProcesses=ASG_PROCESSES)


if __name__ == '__main__':
    main()
