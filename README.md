# EtherJin
EtherJin is an app created with Python Django and Postgres to search and track transactions accross Ethereum blockchain.

## Technologies
This project is created with:
* Python 3.8.11
* Django 3.2
* Django-q 1.3.9
* Redis 3.5.3

## Setup
To run this project for development create .env file as in .env.template file in this repo and use the following command: 

```
docker-compose up -d --build
docker-compose exec django python manage.py runserver 0.0.0.0:8000
```

## Feature
* Login with Linkedin
* Search by address to fetch its transaction data
* Save an address to a folder and track transactions. Addresses will be automatically updated everywith for its transaction data.

