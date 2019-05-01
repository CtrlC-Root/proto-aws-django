#!/bin/bash

set -x

# configure dpkg, apt, apt-get to use non-interactive front-end
export DEBIAN_FRONTEND=noninteractive

# install python virtualenv support
apt-get -y install python3-virtualenv virtualenv

# install postgres
dpkg -l postgresql &> /dev/null
if [ $? -ne 0 ]; then
    sudo apt-get install -y postgresql
    sudo sed -i -e "s/#*\(listen_addresses = \).*\$/\1'*'/" /etc/postgresql/10/main/postgresql.conf
    sudo systemctl restart postgresql.service
fi

systemctl is-active postgresql.service &> /dev/null
if [ $? -ne 0 ]; then
    sudo systemctl enable postgresql.service
    sudo systemctl start postgresql.service
fi

# configure postgres access control
grep -qE "^host\s+frontdesk" /etc/postgresql/10/main/pg_hba.conf
if [ $? -ne 0 ]; then
    echo 'host frontdesk frontdesk 0.0.0.0/0 trust' >> /etc/postgresql/10/main/pg_hba.conf
    sudo systemctl restart postgresql.service
fi

# create database user
sudo -u postgres -i psql -t -c '\du' | cut -d \| -f 1 | grep -qw frontdesk
if [ $? -ne 0 ]; then
    sudo -u postgres -i createuser --login frontdesk
fi

# create database
sudo -u postgres -i psql -lqt | cut -d \| -f 1 | grep -qw frontdesk
if [ $? -ne 0 ]; then
    sudo -u postgres -i createdb -O frontdesk frontdesk
fi
