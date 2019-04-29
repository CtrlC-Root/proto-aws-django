# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.provision "shell", path: "scripts/01-update.sh"
  config.vm.provision "shell", path: "scripts/02-install-python.sh"

  config.vbguest.auto_update = false
  config.vbguest.no_remote = true

  config.vm.define "web" do |web|
    web.vm.hostname = "web"
    web.vm.provider "virtualbox" do |vb|
      vb.memory = 1024
      vb.cpus = 1
    end

    web.vm.provision "shell", path: "scripts/03-local-dev.sh"
    web.vm.provision "file", source: "~/.aws/config", destination: ".aws/config"
    web.vm.provision "file", source: "~/.aws/credentials", destination: ".aws/credentials"
  end
end
