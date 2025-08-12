## Setting up host
sudo apt-get update
sudo apt-get install -y jq net-tools curl git wget vim

## Install Python 3.12 and pip
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get install -y python3.12
sudo apt-get install -y python3-pip
sudo apt-get  install -y python3.12-venv

## Install npm
sudo apt-get install -y npm

## Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh 
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
sudo systemctl enable docker.service
sudo systemctl enable containerd.service

