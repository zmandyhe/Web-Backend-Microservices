### CPSC449-Project Web Backend Engineering
### This is the main repo for the files for CPSC 449's Project 1,2,3.
### The group members for this group are: Mandy He and RJ Kretscmar.

#### The information in this file will reflect different assumptions, instructions, and other meta-data of our project.

##### Design Decisions:
    * We will be using vanilla Flask for the web framework.
    * We will be using sqlite3 for our database.
    * We will be using a Linux-like directory structure for our project. (See Project Structure for more information)

##### Project Structure:
    * etc/ will contain all of the configuration files.
    * bin/ will contain all of the scripts to aid in the project.
    * app/ will contain all of the python code to our microservices.
    * lib/ will contain various libraries (or libary-type files).
    * var/ will contain various changing files; most importatly, the database files.
    * media/ will contain the individual music files and the album art.

##### Database Structure:
Starting with Project 2, we were to implement sharding of the "tracks" database. Three in total. And then there will be one database for the other data, namely the users, playlist, and description tables. The databases, stored in the var/, are named:
    * tracks\_shard0.db
    * tracks\_shard1.db
    * tracks\_shard2.db
    * microservices\_db.db

#### Environment
    - Flask (both the python library and the commandline utility)
    - foreman
    - dot-env
    - sqlite3
    - Kong API Gateway
    - MinIO Object Storage
    - Jinja2 
    - requests

<<<<<<< HEAD
##### TO Run the services, following this process
There are a few scripts and configuration files to help get a new environment ready to go for our microservices. Most of them are locked up in bin/ and etc/, respectively. Here are the steps to set-up the
flask environment and the database with the schema needed to move forward:
=======
##### To run the services, following this process
There are a few scripts and configuration files to help get a new environment ready to go for our microservices. Most of them are locked up in bin/ and etc/, respectively. Here are the steps to set-up the flask environment and the database with the schema needed to move forward:
>>>>>>> be40a26624195955533224077660b3b7002e3a99

    1. To spin up a new database with the appropiate schema, under bin/db\_scripts/new there is a script empty\_sharded\_db.sh which
    you can just run and it'll get a series fresh database files for you to work with.
    2. To run the 4 microservices, migrate to the bin/ directory, run the Procfile through foreman of "foreman start -m all=3", the 4 microservices will run three instances each all on separate ports.
    3. The next thing to start is Kong. The Kong start and initialization scripts are kept with the other scripts in the bin/ directory. First run the *start_kong* script (this requires superuser privileges). Then run all of the initializations scripts to set up all the Upstreams, the Targets, the Services, and the Routes. It doesn't matter in which order you run that, just make sure they're all executed once.
    4. To start MINIO: go to /Minio folder with executable file and sub-folders, then to go terminal, and
	run minio:
	"./minio server start object storage server"
      Minio server will run at http://127.0.0.1:9000, and mp3 files are stored in th folder of /tracks
      Use the following credentials to access the minio server bucket:
         -AccessKey: 54AUW87M5DUD0B9UBR1X 
         -SecretKey: s28mRRzRRhJcJv84MxzEyNaVt2nTwejSkWuGoBr8 
<<<<<<< HEAD
    4. to generate a xspf playlist, the script is located in /app/xspf.py. Go to /app folder, from terminal, run "python xspf.py", it will run in local host.
       run this endpoint: http://127.0.0.1:8000/playlist/1. The sample playlist xml file is xspf-playlist.xml.

#### xspf Microservice:
    *to run it, go to /app
    *in terminal, run: python xspf.py
    *http://127.0.0.1:8000/playlist/1 to generate a xspf playlist.

#### Environment
    * Make sure that you have Flask (both the python library and the commandline utility), foreman, dot-env, and sqlite3 downloaded and installed.
    * To spin up a new database with the appropiate schema, under bin/db\_scripts/new there is a empty empty\_sharded\_db.sh which
    you can just run and it'll get a fresh database file for you to work with.
    * After that, migrate to the bin/ directory, run the Procfile through foreman.
    * Finally, you are ready to enjoy.
=======
    5. To generate a xspf playlist, the script is located in /app/xspf.py. Go to /app folder, from terminal, run "python xspf.py", it will run in local host.
       run this endpoint: http://127.0.0.1:8080/playlist/1. The sample playlist xml file is xspf-playlist.xml.

#### xspf Microservice:
    TODO: Finish xspf service documentation.
>>>>>>> be40a26624195955533224077660b3b7002e3a99

##### Tracks Microservice:
To learn more about the Tracks API and how to use it, please refer to the root page of the microservice after starting it up. It will have the most up-to-date information on all the new features and a general
guide on how to use it.

##### Playlist Microservice:
To learn more about the Playlist API and how to use it, please refer to the root page of the microservice after starting it up. It will have the most up-to-date information on all the new features and a general
guide on how to use it.

##### Users Microservice:
users.py: python scripts to crate datatable, table, create new user, update user password, delete user, view user profile

##### Description Microservices
desc.py: python script to set and retrieve a user's description of a track.
