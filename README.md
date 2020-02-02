# Overview

The Coronavirus Tracker Scrapper

## Requirements

This project requires Python 3.

## Getting Started

### 1. Setup virtual environment.
    # Create new virtualenv.
    $ python3 -m venv .venv

    # Change to virtualenv.
    $ source .venv/bin/activate

### 2. Install requirements
    # Run this in the project directory.
    #
    # Upgrade pip
    $ pip install -U pip

    # Install requirements
    $ pip install -r requirements.txt

### 3. Connect to db.
    Add these to .env (Should be in the same directory as main.py).

    DB_HOST = ""
    DB_PORT = 3306
    DB = ""
    DB_USER = ""
    DB_PASSWORD = ""
    NEWSAPI_TABLE = ""


### 4. Start scrapping.
    $ python main.py
