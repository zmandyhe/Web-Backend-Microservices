#!/bin/bash
# This is a small script to create the schema for a series of new databases.
# It creates three (3) tracks shard databases, as per the project instruction,
# and then creates the database to hold the other data such as users, playlists,
# and descriptions. NOTE: These databases are not going to be initalized with data.

echo "Creating databases...";
echo "Creating var/tracks_shard0.db";
sqlite3 ../../../var/tracks_shard0.db < ./tracks_shard_generator.sql;
echo "Done!";
echo "Creating var/tracks_shard1.db";
sqlite3 ../../../var/tracks_shard1.db < ./tracks_shard_generator.sql;
echo "Done!";
echo "Creating var/tracks_shard2.db";
sqlite3 ../../../var/tracks_shard2.db < ./tracks_shard_generator.sql;
echo "Done!";
echo "Creating var/microservices_db.db";
sqlite3 ../../../var/microservices_db.db < ./microservices_db_generator.sql;
echo "Done!";
echo "All databases created successfully!"

