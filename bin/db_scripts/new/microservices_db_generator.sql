-- This file defines the schema for a the database that will hold non-sharded information. 
-- That is to say the users, playlist, and description tables. To be clear, unlike the
-- 3 sharded track databases, the will be one database with 3 tables.

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
    DROP TABLE IF EXISTS playlists;
    CREATE TABLE playlists (
        playlist_title VARCHAR NOT NULL,
        track_url VARCHAR,
        guid GUID NOT NULL,
        username VARCHAR,
        description VARCHAR,
	FOREIGN KEY(guid)
        REFERENCES tracks (guid) 
	    ON UPDATE CASCADE 
	    ON DELETE CASCADE
    );

    DROP TABLE IF EXISTS users;
    CREATE TABLE users (
        username VARCHAR NOT NULL UNIQUE PRIMARY KEY,
        pwd_hash VARCHAR,
        displayname VARCHAR,
        email VARCHAR NOT NULL UNIQUE,
        url VARCHAR
    );

    DROP TABLE IF EXISTS desc;
    CREATE TABLE desc (
        username VARCHAR,
        trackdesc VARCHAR,
	track_url VARCHAR,
	FOREIGN KEY(track_url) 
	REFERENCES tracks (track_url) 
	    ON UPDATE CASCADE 
	    ON DELETE CASCADE
    );
    COMMIT;
