# proto-aws-django

Deploy a Django application to AWS with support for zero downtime rolling
updates.

## Requirements

* Python 3.5+
* VirtualBox
* Vagrant
* Packer

## Vagrant

Create and provision the virtual machine.

```bash
vagrant up
vagrant reload
```

The virtual machine copies your `~/.aws/config` and `~/.aws/credentials` files
to the `vagrant` user's home folder. However you need to manually start an SSH
agent and forward it to the VM if you want to be able to use your SSH key.

```bash
ssh-add
vagrant ssh -- -A
```

Navigate to the `/vagrant` folder which is synchronized with the top-level
project folder.

```bash
cd /vagrant
```

Create a python virtualenv and install dependencies.

```bash
virtualenv -p $(which python3) env
source env/bin/activate
pip install -r requirements.txt
```

## Provision

Here's what you need to do to start from scratch:

* Locate the default VPC and Subnets or [create them](https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html#default-vpc-components).
* Locate or create a Route53 hosted zone for a top-level domain.
* Locate or create a wildcard SSL certificate in the Certificate Manager.
* Build the Web AMI (`packer build packer/web.json`).
* Build the application (in vagrant `create_build.py`).
* Set SSM parameters (see below).
* Create the CloudFormation stack (see below).
* Deploy the initial build (`deploy_build.py`).
* Verify the application is reachable at the configured domain.

Here's how you set secret and plain-text SSM parameters:

```bash
aws ssm put-parameter --name '/Frontdesk/DatabaseMasterPassword' \
  --description 'RDS DBInstance MasterUserPassword' \
  --value 'something_secure_and_secret' \
  --type 'SecureString' \
  --tags 'Key=Project,Value=Frontdesk'

aws ssm put-parameter --name '/Frontdesk/WebImageId' \
  --description 'Web ASG AMI ID' \
  --value 'ami-ABCDWXYZ' \
  --type 'String' \
  --tags 'Key=Project,Value=Frontdesk'
```

Here's the SSM parameters you need to set:

* `VpcId` (String) AWS VPC Id
* `PrimarySubnetId` (String) AWS VPC Primary Subnet Id
* `SecondarySubnetId` (String) AWS VPC Secondary Subnet Id
* `CertificateArn` (String) Wildcard SSL Certificate ARN (`*.example.com`)
* `HostedZoneId` (String) Route53 hosted zone for top-level domain
* `DomainName` (String) Second level domain (i.e. `demo.example.com`)
* `WebImageId` (String) Web ASG AMI Id (i.e. `ami-ABCDWXYZ`)
* `KeyName` (String) SSH KeyPair Name
* `SecretKey` (SecureString) Django `SECRET_KEY` setting
* `MasterDatabasePassword` (SecureString) Database master user password

Here's how you create the CloudFormation stack:

```bash
aws cloudformation create-stack --stack-name Frontdesk \
  --capabilities CAPABILITY_NAMED_IAM \
  --template-body file://cloudformation/frontdesk.yaml
```

## Update Web AMI

Build a new AMI using Packer:

```bash
packer validate packer/web.json
packer build packer/web.json
```

Update the `WebImageId` parameter in SSM:

```bash
aws ssm put-parameter --name '/Frontdesk/WebImageId' \
  --value 'ami-ABCDWXYZ' \
  --type 'String' \
  --overwrite
```

Trigger a rolling update of web instances by updating the stack:

```bash
aws cloudformation update-stack --stack-name Frontdesk \
  --capabilities CAPABILITY_NAMED_IAM \
  --template-body file://cloudformation/frontdesk.yaml
```

## Create Build

Update the `frontdesk` application and the version in `setup.py` to reflect the
changes made. Create a build:

```bash
./create_build.py --project-path pkg/frontdesk
```

## Deploy Build

Deploy a build:

```bash
./deploy_build.py --app-build ./frontdesk-0.1.pex
```

## Deprovision

Generally the exact opposite of provisioning with a few extra steps:

* Delete content of deployment bucket
* Delete stack
* Delete SSM parameters
* Deregister AMIs
* Delete AMI snapshots

## References

Tools and frameworks:

* [Pex](https://pex.readthedocs.io/en/stable/index.html)
* [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

AWS:

* [SSM Secure String](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html#dynamic-references-ssm-secure-strings)
