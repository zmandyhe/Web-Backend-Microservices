-- This is the schema file for the track shard databases. Since all the databases are going to be the same
-- (aside from the actual names), the unqiueness of each database will come from the script that creates
-- the shards.

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
    DROP TABLE IF EXISTS tracks;
    CREATE TABLE tracks (
        guid GUID NOT NULL PRIMARY KEY,
        title VARCHAR NOT NULL,
        album VARCHAR NOT NULL,
        artist VARCHAR NOT NULL,
        len VARCHAR NOT NULL, 
        track_url VARCHAR NOT NULL,
        art_url VARCHAR
    );
    COMMIT;
