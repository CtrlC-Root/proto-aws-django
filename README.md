# proto-aws-django

Deploy a Django application to AWS.

## Requirements

* Python 3.5+
* Packer

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
doit task_update_web_ami
```

## References

Tools:

* [DoIt](http://pydoit.org/)
* [Pex](https://pex.readthedocs.io/en/stable/index.html)

Frameworks and libraries:

* [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
