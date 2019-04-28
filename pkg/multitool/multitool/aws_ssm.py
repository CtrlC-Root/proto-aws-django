import boto3


def update_ssm_parameter(name, type, value):
    client = boto3.client('ssm')
    client.put_parameter(Name=name, Type=type, Value=value, Overwrite=True)
