#!/bin/bash

set -x
set -e

# configure dpkg, apt, apt-get to use non-interactive front-end
export DEBIAN_FRONTEND=noninteractive

# install python virtualenv support
apt-get -y install python3-virtualenv virtualenv
