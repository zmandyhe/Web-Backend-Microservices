### Web Backend Engineering
### Contributors: Mandy He and RJ Kretscmar.

#### The information in this file will reflect different assumptions, instructions, and other meta-data of our project.

##### Design Decisions:
    * We will be using vanilla Flask for the web framework.
    * We will be using ScyllaDB, A Cassandra type of wide columndatabase.
    * We will be using a Linux-like directory structure for our project. (See Project Structure for more information)

##### Project Structure:
    * etc/ will contain all of the configuration files.
    * bin/ will contain all of the scripts to aid in the project.
    * app/ will contain all of the python code to our microservices.
      -xspf.py
      -users.py
      -tracks.py
      -playlists.py
      -desc.py
    * lib/ will contain various libraries (or libary-type files).
    * var/ will contain various changing files; we keeps the project 2 Sqlite3 database files there.
    * media/ will contain the individual music files and the album art.
    * docs/ contains screenshots for memcached before/afteer and microservices operations screenshots.

##### Database Structure:
The keyspace of "xspf" has 2 Cassandra tables as follows. Visit ../docs/cqlsh-creating-tables-and-verify-tables.txt to view two tables structures.
  * users_by_username
  * playlists_by_playlist_id_and_username

#### Environment
    - Flask
    - foreman
    - dot-env
    - Jinja2
    - requests
    - memcached and pymemcache
    - Docker
    - ScyllaDB
    - Cassandra
    - DataStax's Python Driver for Apache Canssandra
    - MinIO Object Storage
    - Kong API Gateway

#### Steps to generate a XSPF playlist:
    1. start the scylla database from any directory, then verify it do start:
    ```
    $docker start scylla
    $docker exec -it scylla nodetool status
    ```
    2. Start the memcache server running on local host with port number of 11211
    ```
    sudo service memcached start
    ```
    record the memcache statistics before and after the xspf service uses memcache.
    ```
    $ telnet localhost 11211
      stats
    ```
    3. Run the 4 backend microservices and the xspf playlist service, migrate to the bin/ directory, run the Procfile through foreman of "foreman start", the 4 microservices will run three instances each all on separate ports. To get the xspf playlist xml output, visit:
    http://127.0.0.1:5400/playlist/1
      ```
      foreman start
      ```
      ports assignments are:
      ```
      21:31:46 users.1     |  * Running on http://127.0.0.1:5200/
      21:31:46 tracks.1    |  * Running on http://127.0.0.1:5000/
      21:31:46 playlists.1 |  * Running on http://127.0.0.1:5100/
      21:31:46 desc.1      |  * Running on http://127.0.0.1:5300/
      ```

    4. Run xspf.py from ./app/xspf.py as follows. The service is running on http://127.0.0.1:5400/playlist/1. The output file is xspf-playlist_1.xml.
    ```
    python3 xspf.py
    ```
    5. Media data has been saved to MiNIO remote server. To start MINIO: go to /Minio folder with executable file and sub-folders, then to go terminal, and run minio as the following:
    ```
	   ./minio server start object storage server
    ```
      Minio server will run at http://127.0.0.1:9000, and mp3 files are stored in the folder of /tracks
      Use the following credentials to access the minio server bucket:
      ```
         -AccessKey: 54AUW87M5DUD0B9UBR1X
         -SecretKey: s28mRRzRRhJcJv84MxzEyNaVt2nTwejSkWuGoBr8
      ```
#### Query Screenshots
  There are some saved screenshots during the CRUD process from each microservices' http endpoints.
  They are under ../docs/
  - users
  - playlists
  - tracks
  - desc
  - memcached
  - xspf playlists xml

#### xspf Microservice:
xspf.py: To generate a xspf playlist, the script is located in /app/xspf.py. Go to /app folder, from terminal, run "python xspf.py", it will run in local host.
run this endpoint: http://127.0.0.1:5400/playlist/1. The sample playlist xml file is xspf-playlist.xml.

##### Tracks Microservice:
tracks.py: To learn more about the Tracks API and how to use it, please refer to the root page of the microservice after starting it up. It will have the most up-to-date information on all the new features and a general
guide on how to use it.

##### Playlist Microservice:
playlists.py: To learn more about the Playlist API and how to use it, please refer to the root page of the microservice after starting it up. It will have the most up-to-date information on all the new features and a general
guide on how to use it.

##### Users Microservice:
users.py: python scripts to crate datatable, table, create new user, update user password, delete user, view user profile

##### Description Microservices
desc.py: python script to set and retrieve a user's description of a track.
