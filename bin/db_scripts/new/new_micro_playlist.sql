-- This file defines the schema for a new database. It contains four tables; one for
-- each of our microservices: Tracks, Playlists, Users, and Descriptions.

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
    DROP TABLE IF EXISTS tracks;
    CREATE TABLE tracks (
        title VARCHAR NOT NULL,
        album VARCHAR NOT NULL,
        artist VARCHAR NOT NULL,
        len VARCHAR NOT NULL, 
        track_url VARCHAR NOT NULL,
        art_url VARCHAR,
        PRIMARY KEY(title, album, artist)
    );

    DROP TABLE IF EXISTS playlists;
    CREATE TABLE playlists (
        playlist_title VARCHAR NOT NULL PRIMARY KEY,
        track_url VARCHAR,
        username VARCHAR,
        description VARCHAR,
	FOREIGN KEY(track_url) 
	  REFERENCES tracks (track_url) 
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
