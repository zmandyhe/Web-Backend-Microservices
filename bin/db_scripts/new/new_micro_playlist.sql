-- This file defines the schema for a new database. It contains four tables; one for
-- each of our microservices: Tracks, Playlists, Users, and Descriptions.
-- TODO: Figure out Primary/Forign Keys. Finish the rest of the tables.

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
    DROP TABLE IF EXISTS tracks;
    CREATE TABLE tracks (
        title VARCHAR NOT NULL,
        album VARCHAR NOT NULL,
        artist VARCHAR NOT NULL,
        len VARCHAR NOT NULL, -- TODO: Keep as VARCHAR?
        track_url VARCHAR NOT NULL,
        art_url VARCHAR,
        PRIMARY KEY(title, album, artist)
    );
    COMMIT;
