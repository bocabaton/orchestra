# PyEngine - Installation

* [CentOS](https://github.com/pyengine/pyengine/blob/master/docs/INSTALL.md#centos)
* Ubuntu
* Amazon Linux

## CentOS
### 1. Install Yum Packages
~~~bash
yum install python python-pip mariadb MySQL-python httpd mod_wsgi git
~~~

### 2. Install PIP Packages
~~~bash
pip install django django-log-request-id dicttoxml xmltodict routes rsa pytz
~~~

### 3. MariaDB Installation (Optional)
* Install MariaDB Package
~~~bash
yum install mariadb-server
~~~

* Update Settings (/etc/my.cnf)
~~~text
[mysql]
...
default-character-set = utf8

[mysqld]
...
init_connect="SET collation_connection=utf8_general_ci"
init_connect="SET NAMES utf8"
character-set-server=utf8
collation-server=utf8_general_ci
skip-character-set-client-handshake

[client]
...
default-character-set = utf8

[mysqldump]
...
default-character-set = utf8
~~~

* Restart MariaDB
~~~bash
systemctl start mariadb.service
systemctl enable mariadb.service
~~~

* Set Root Password & Login
~~~bash
mysqladmin -u root password '<password>'
mysql -u root -p
~~~

* Create Database & User
~~~mysql
create database pyengine;
grant all privileges on pyengine.* to pyengine@'%' identified by '<password>' with grant option;
grant all privileges on pyengine.* to pyengine@'localhost' identified by '<password>' with grant option;
~~~

### 4. Download PyEngine Source
~~~bash
git clone https://github.com/pyengine/pyengine.git identity
~~~

## 5. Change Log Permissions
~~~bash
mkdir -p /var/log/pyengine
chown -R apache:apache /var/log/pyengine
~~~

## 6. Update Pyengine Settings
~~~text
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pyengine',
        'USER': 'pyengine',
        'PASSWORD': '<password>',
        'HOST': 'localhost',
    }
}

LOGGING = {
            ...
            'filename' : '/var/log/pyengine/pyengine.log',
            ...
}
~~~

## 7. DB Sync
~~~bash
cd /opt/pyengine
python manage.py makemigrations
python manage.py migrate
~~~

## 8. Create Root User
~~~bash
cd /opt/pyengine/bin
python create_root.py <root_password>
~~~

## 9. Set Apache Configuration (/etc/httpd/conf.d/pyengine.conf)
~~~text
<VirtualHost *:80>
        Alias /pyengine/static/ /opt/pyengine/static/
        <Directory /opt/pyengine/static>
            Require all granted
        </Directory>

        WSGIScriptAlias /pyengine /opt/pyengine/pyengine/wsgi.py
        <Directory /opt/pengine/pyengine>
        <Files wsgi.py>
            Require all granted
        </Files>
        </Directory>

        AddDefaultCharset UTF-8
</VirtualHost>
~~~

## 10. Start Apache Daemon
~~~bash
systemctl restart httpd.service
systemctl enable httpd.service
~~~
