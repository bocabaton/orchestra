# Cloud Orchestration Engine

<img src="https://raw.githubusercontent.com/bocabaton/orchestra/master/docs/architecture/concept.png">

# Easy Installation

## Ubuntu

There are easy installation guide when you uses Ubuntu.

* Install Jeju tools

~~~bash
apt-get update
apt-get -y install python-dev python-pip expect gcc git
pip install jeju --upgrade
~~~

* Install Orchestra from source

~~~bash
jeju -m orchestra.md
~~~

* Install Web Dashboard

~~~bash
cd /opt/orchestra/static
git clone https://github.com/bocabaton/orchestra-ui.git dashboard
~~~

* Update Basic information

After Basic Installation, you needs to update default information for Database.

~~~bash
cd /opt/orchestra/bin
python create_user.py <account> <password>
~~~

for example,
~~~bash
cd /opt/orchestra/bin
python create_user.py root 123456
~~~

This is an account for Orchetra, not root account of Linux OS.
Now you can visit your web dashboard.

~~~text
http://<your server ip>/static/dashboard
~~~
