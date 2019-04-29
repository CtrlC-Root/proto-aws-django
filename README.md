# proto-aws-django

Deploy a Django application to AWS with support for zero downtime rolling
updates.

## Requirements

* Python 3.5+
* VirtualBox **6.0.6** (w/ matching Guest ISO)
* Vagrant
* Packer

**NOTE**: There are bugs in the `vboxsf` shared filesystem driver that are
fixed in VirtualBox 6.0.6 host and guest modules. Older versions won't let you
run `doit` in the `/vagrant` directory.

## Quick Start

Create a python virtualenv, install dependencies, and link utility packages.

```bash
virtualenv -p $(which python3) env
source env/bin/activate
pip install -r requirements.txt
python pkg/multitool/setup.py develop
```

Use `doit` to list and run tasks.

```bash
doit list
doit update_web_ami
```

## Vagrant

TODO: why this matters, python version

Install necessary vagrant plugins.

```bash
vagrant plugin install vagrant-vbguest
```

Create and provision the virtual machine.

```bash
vagrant up
vagrant vbguest --no-provision
vagrant reload
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

* [DoIt](http://pydoit.org/)
* [Pex](https://pex.readthedocs.io/en/stable/index.html)

Frameworks and libraries:

* [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
