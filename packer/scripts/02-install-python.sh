#!/bin/bash

set -x
set -e

# configure dpkg, apt, apt-get to use non-interactive front-end
export DEBIAN_FRONTEND=noninteractive

# install python 3
apt-get -y install python3
