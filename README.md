# proto-aws-django

Deploy a Django application to AWS with support for zero downtime rolling
updates.

## Requirements

* Python 3.5+
* VirtualBox
* Vagrant
* Packer

## Quick Start

Create a python virtualenv, install dependencies, and link utility packages.

```bash
virtualenv -p $(which python3) env
source env/bin/activate
pip install -r requirements.txt
```

## Vagrant

TODO: why this matters, python version

Create and provision the virtual machine.

```bash
vagrant up
```

The virtual machine copies your `~/.aws/config` and `~/.aws/credentials` files
to the `vagrant` user's home folder. However you need to manually start an SSH
agent and forward it to the VM if you want to be able to use your SSH key.

```bash
ssh-add
vagrant ssh -- -A
```

Lastly you need to navigate to the `/vagrant` folder which is synchronized
with the top-level project folder.

```bash
cd /vagrant
```

Now you can follow the regular environment setup instructions from above.

## References

Tools:

* [Pex](https://pex.readthedocs.io/en/stable/index.html)
* [Vagrant VBGuest](https://github.com/dotless-de/vagrant-vbguest)

Frameworks and libraries:

* [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

CloudFormation:

* [SSM Secure String](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html#dynamic-references-ssm-secure-strings)
