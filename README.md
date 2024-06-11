# FitHub

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Running the Application](#running-the-application)
5. [Usage](#usage)
6. [Managing the Database](#managing-the-database)
7. [Additional Information](#additional-information)


## Introduction
Description:
This is FitHub, a web-based application designed to help you become a fitter and better version of yourself.
FitHub offers a range of features aimed at providing comprehensive fitness and health support.


## Prerequisites
- Python 3.x
- pip (Python package installer)

## Installation

1. clone the repository: ```git clone https://github.com/Elgran666/FitHub_V1.git```
2. then cd into it: ```cd FitHub_V1```

4. install flask: ```pip install flask```

## Running the Application

1. run the flask server: ```flask run```


2. open the application
   - open your web browser and navigate to the url provided by the flask server, typically http://127.0.0.1:5000

## Usage

1. create an account
   - open the registration page
   - go through sign-up flow
   - click "create account" to create your account

2. sign in
   - open the login page
   - enter your username and password
   - click "sign in" to access your account

## Managing the Database

if you need to clear the database, follow these steps:

1. open sqlite3: ```sqlite3 fithub.db```

2. clear tables

   2.1 clear weight_entries table: ```DELETE FROM weight_entries;```

   2.2 reset counter for weight_entries table: ```UPDATE sqlite_sequence SET seq = 0 WHERE name = 'weight_entries';```

   2.3 clear users table: ```DELETE FROM users;```

   2.4 reset counter for users table: ```UPDATE sqlite_sequence SET seq = 0 WHERE name = 'users';```

   2.5 Optimize the database: ```VACUUM;```

## Additional Information
- for any issues or bugs, check the flask server logs for error messages and debug information
