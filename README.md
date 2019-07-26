# Arancia - Distributed Key Value Store

This project targets on creating a distributed key-value store based on 2PC protocol with consistent hashing in order to maintain data consistency and high availability. 

### Prerequisites

What things you need to install the software and how to install them

```
Vagrant
```
[Download vagrant for macOS](https://releases.hashicorp.com/vagrant/2.2.5/vagrant_2.2.5_x86_64.dmg)

```
virtualbox 5.2.30 
```
[Download virtualbox for macOS](https://download.virtualbox.org/virtualbox/5.2.30/VirtualBox-5.2.30-130521-OSX.dmg)

### Installing

A step by step series of examples that tell you have to get a development env running


```
Install the Vagrant using the download link
```

```
Install virtualbox using the download link
```

```
cd deploy/
```

Creates the Ubuntu virtual machine using the Vagrantfile
```
vagrant up
```

SSH into the virtual machine
```
vagrant ssh
```

Folder which has symlink with local machine folder
```
cd /vagrant
```

Install the Go Library
```
go get github.com/elazarl/goproxy
```

Creates a python3 virtualenv
```
mkvirtualenv --python=python3 <NAME_OF_ENV>
```

Install the python dependencies
```
pip3 install -r requirements.txt
```

Use this command to deactivate the python virtual environment
```
deactivate
```

Use this command to activate the python virtual environment
```
workon <NAME_OF_ENV>
```

Similarly, install all the prerequisites.

## Running the tests

Use this command from root directory to start the Go Proxy server 
```
go run proxy.go
```

Use this command from /server to start the Gunicorn Server
```
gunicorn --bind=0.0.0.0:8000 --log-level=debug wsgi --reload
```

Start the Celery Worker from /server
```
celery -A send_email worker --loglevel=info
```

**API Calls with documentation will be updated soon. Moreover how to use CURL or POSTMAN to send the request shall be explained.**

## Deployment

Not Deployed.

## Versioning

I use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/dhruvp-8). 

## Authors

* **Dhruv Patel** - *Initial work* - [dhruvp-8](https://github.com/dhruvp-8)


## License


## Acknowledgments
