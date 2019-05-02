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

TODO:

* Locate or create VPC and two Subnets
* Locate or create a Route53 hosted zone
* Locate or create a wildcard Certificate
* Build the web AMI
* Build the application
* Set SSM parameters
* Create stack
* Upload application to deployment bucket (before ASG is created)
* Verify application works

## Create Build

Update the `frontdesk` application and the version in `setup.py` to reflect the
changes made. Create a build:

```bash
./create_build.py --project-path pkg/frontdesk
```

## Deploy Build

Deploy a build to the web instances in the ASG one at a time.

```bash
./deploy_build.py --app-build ./frontdesk-0.1.pex
```

## Deprovision

TODO:

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
