#!/bin/bash

set -x
set -e

# configure dpkg, apt, apt-get to use non-interactive front-end
export DEBIAN_FRONTEND=noninteractive

# update packages
apt-get update
apt-get -y upgrade
apt-get -y dist-upgrade
