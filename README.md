# EtherJin
EtherJin is an app created with Python Django and Postgres to search and track transactions accross the Ethereum blockchain.

## Technologies
This project is created with:
* Python 3.8.11
* Django 3.2
* Django-q 1.3.9
* Redis 3.5.3

## Setup
To run this project for development, create an .env file as in the .env.template file in this repo and use the following command: 

```
docker-compose up -d --build
docker-compose exec django python makemigrations
docker-compose exec django python migrate
docker-compose exec django python manage.py runserver 0.0.0.0:8000
docker-compose exec django python manage.py create_index
```
## Features
* Login with Linkedin
* Search by address to fetch its transaction data
* Save an address to a folder and track transactions. Saved addresses will be automatically updated everyday for their transaction data.
### Features in development
* Analytics for address folders 
* Payment integration for the premium usership 
* public and private user profiles 
* Platform and email notifications
