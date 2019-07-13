# Update the apt package manager
sudo apt-get update

# Install Nginx
sudo apt-get -y install nginx

# Install the python-git client for salt to get the config from the repo
sudo apt-get -y install python-git
sudo apt install -y python3-pip

# Install Basic Tools
sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" install git

# Install Golang
GOSOURCE=https://storage.googleapis.com/golang/go1.9.linux-amd64.tar.gz
GOTARGET=/usr/local
GOPATH=\$HOME/go
PROFILE=/vagrant/.profile

# Download Go tools to $GOTARGET/go
curl -sSL $GOSOURCE -o /tmp/go.tar.gz
tar -xf /tmp/go.tar.gz -C $GOTARGET
rm /tmp/go.tar.gz

# Apply Environment Configuration to the .profile
printf "\n" >> $PROFILE
printf "# golang configuration\n" >> $PROFILE
printf "export GOROOT=$GOTARGET/go\n" >> $PROFILE
printf "export GOPATH=$GOPATH\n" >> $PROFILE
printf "export PATH=\$PATH:$GOTARGET/go/bin:$GOPATH/bin\n" >> $PROFILE

# Install Go Compiler
sudo apt-get -y install gccgo-go