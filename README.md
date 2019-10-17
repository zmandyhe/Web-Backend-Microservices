### CPSC449-Project1
### This is the main repo for the files for CPSC 449's Project 1.
### The group members for this group are: Mandy He and RJ Kretscmar.

#### The information in this file will reflect different assumptions, instructions, and other meta-data of our project.

##### Design Decisions:
   - We will be using vanilla Flask for the web framework.
   - We will be using sqlite3 for our database.
   - We will be using a Linux-like directory structure for our project. (See Project Structure for more information)

##### Project Structure:
   - etc/ will contain all of the configuration files.
   - bin/ will contain all of the scripts to aid in the project.
   - app/ will contain all of the python code to our microservices.
   - lib/ will contain various libraries (or libary-type files).
   - var/ will contain various changing files; most importatly, the database file.

##### Tips on Making the Environment Useable Out-Of-The-Box
There are a few scripts and configuration files to help get a new environment ready to go for our microservices. Most of them are locked up in bin/ and etc/, respectively. Here are the steps to set-up the
flask environment and the database with the schema needed to move forward:
    - Make sure that you have Flask (both the python library and the commandline utility), foreman, dot-env, and sqlite3 downloaded and installed.
    - To spin up a new database with the appropiate schema, under bin/db\_scripts/new there is a make\_empty\_db.sh which
    you can just run and it'll get a fresh database file for you to work with.
    - After that, migrate to the bin/ directory, run the Procfile through foreman.
    - Finally, you are ready to enjoy.

##### Tracks Microservice:
To learn more about the Tracks API and how to use it, please refer to the root page of the microservice after starting it up. It will have the most up-to-date information on all the new features and a general
guide on how to use it.

##### Playlist Microservice:
To learn more about the Playlist API and how to use it, please refer to the root page of the microservice after starting it up. It will have the most up-to-date information on all the new features and a general
guide on how to use it.

##### Users Microservice:
users.py: python scripts to crate dataable, table, create new user, update user password, delete user, view user profile

##### Description Microservices
desc.py: python script to set and retrieve a user's description of a track.
