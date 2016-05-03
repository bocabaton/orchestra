# Rebuild data

# Environment

## environment table

Keyword | Value     | Description
----    | ----      | ----
REPO | /opt/orchestra | Project name

## Clean up database

~~~bash
mysql -u root -e "drop database pyengine" 
~~~

## Create database

~~~bash
mysql -u root -e "create database pyengine character set utf8 collate utf8_general_ci"
~~~


# Recreate table

~~~bash
cd ${REPO}/pyengine/migrations/
rm -f 0*.py
rm -f *.pyc


cd ${REPO}
python manage.py makemigrations
python manage.py migrate
~~~
