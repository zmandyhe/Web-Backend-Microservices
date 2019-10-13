### CPSC449-Project1
### This is the main repo for the files for CPSC 449's Project 1.
### The group members for this group are: MH and RJ.

#### The information in this file will reflect different assumptions, instructions, and other meta-data of our project.

##### Design Decisions:
   - We will be using vanilla Flask for the web framework.
   - We will be using sqlite3 for our database.
   - We will be using a Linux-like directory structure for our project. (See Project Structure for more information)

##### Project Structure:
   - etc/ will contain all of the configuration files.
   - bin/ will contain all of the scripts to aid in the project.
   - app/ will contain all of the python code to our microservices. (NOTE: May or may not go with this idea.)
   - lib/ will contain micilanious libraries (or libary-type files).
   - var/ will contain various changing files, most importatly is the database file.
   - usr/ will contain various static files, most of which will be images.


##### Users Microservice:
users.py: python scripts to crate dataable, table, create new user, update user password, delete user, view user profile
users.db: contains users table to store user profile
users.csv: the original datasets to inject to database for test
