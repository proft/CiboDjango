# CiboDjango
Cibo is an example of backend side of food order service.

It contains Manager account to control new orders and API endpoints for mobile clients. 

iOS version coming soon.

It is written on Django (3.2.5) and Python 3.8.9.

## Create virtual environment 

Create virtual environment 

``
python3 -m venv cibo
``

Install dependencies

``
pip install -r r.txt 
``

Apply migrations

``
python manage.py migrate
``

Create admin user

``
python manage.py createsuperuser
``

Run local web server

``
python manage.py runserver
``