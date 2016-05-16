# Pyengine

## Prerequisite

Keyword | Value     | Description
----    | ----      | ----
PROJECT | orchestra | Project name
 
# Installation

## Install libraries

Pyengine is based on apache and python django framework

~~~bash
apt-get update
apt-get install -y git python-dev python-pip mariadb-server apache2 libapache2-mod-wsgi python-mysqldb libyaml-cpp-dev libyaml-dev python-paramiko
~~~

## Install BPMN library

Workflow Engine is based on BPMN library

~~~bash
git clone https://github.com/knipknap/SpiffWorkflow.git
cd SpiffWorkflow
python setup.py install
~~~

## Install PIP libraries for django

~~~bash
pip install django
pip install django-log-request-id
pip install dicttoxml
pip install xmltodict
pip install routes
pip install rsa
pip install pytz
pip install pyyaml
pip install boto3
~~~

## Download source

Download pyengine source

~~~bash
cd /opt/
git clone https://github.com/pyengine/orchestra.git ${PROJECT}
~~~

## Update python module path environment

edit /usr/local/lib/python2.7/site-packages/pyengine.pth

~~~text
/opt/${PROJECT}
~~~

# Update Configuration

## Update Apache configuration

edit /etc/apache2/conf-available/pyengine.conf

~~~text
<VirtualHost *:80>
    Alias /static    /opt/${PROJECT}/static
    <Directory /opt/${PROJECT}/static>
        Require all granted
    </Directory>

    WSGIScriptAlias / /opt/${PROJECT}/pyengine/wsgi.py
    WSGIPassAuthorization On

    <Directory /opt/${PROJECT}/pyengine>
    <Files wsgi.py>
        Require all granted
    </Files>
    </Directory>

    AddDefaultCharset UTF-8
</VirtualHost>
~~~

Enable the pyengine

~~~bash
a2enconf pyengine
~~~

# Create Database

Create pyengine database

~~~bash
mysql -u root -e "create database pyengine character set utf8 collate utf8_general_ci"
~~~

## Update django DB

~~~bash
mkdir /var/log/pyengine
chown -R www-data:www-data /var/log/pyengine

cd /opt/${PROJECT}
python manage.py makemigrations
python manage.py migrate
~~~

# Restart Apache

~~~bash
rm /var/log/pyengine/api.log
service apache2 restart
~~~
