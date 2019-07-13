# Update the apt package manager
sudo apt-get update

# Install Nginx
sudo apt-get -y install nginx

# Install the python-git client for salt to get the config from the repo
sudo apt-get -y install python-git
sudo apt install -y python3-pip

# Install Basic Tools
sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" install git

# Install Go [v1.9.1]
sudo apt-get remove gccgo-go
curl -O https://storage.googleapis.com/golang/go1.9.1.linux-amd64.tar.gz
tar -xvf go1.9.1.linux-amd64.tar.gz
mv go /usr/local

# Set the Go Environment
touch /vagrant/.bash_profile
echo "export PATH=$PATH:/usr/local/go/bin" >> /vagrant/.bash_profile
echo `export GOPATH=/vagrant:$PATH` >> /vagrant/.bash_profile
export GOPATH=/vagrant
mkdir -p "$GOPATH" 

# Install Go Compiler
sudo apt-get -y install gccgo-go

# Remove the go tar file
rm  go1.9.1.linux-amd64.tar.gz