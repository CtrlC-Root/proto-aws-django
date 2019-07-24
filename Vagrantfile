# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.provision "shell", path: "scripts/01-update.sh"
  config.vm.provision "shell", path: "scripts/02-install-python.sh"

  config.vm.define "web" do |web|
    web.vm.hostname = "web"
    web.vm.provider "virtualbox" do |vb|
      vb.memory = 1024
      vb.cpus = 1
    end

    web.vm.provision "shell", path: "scripts/03-local-dev.sh"
    web.vm.provision "file", source: "~/.aws/config", destination: ".aws/config"
    web.vm.provision "file", source: "~/.aws/credentials", destination: ".aws/credentials"
    web.vm.network :forwarded_port, guest: 5432, host: 5432 # postgres
    web.vm.network :forwarded_port, guest: 6379, host: 6379 # redis
  end
end
