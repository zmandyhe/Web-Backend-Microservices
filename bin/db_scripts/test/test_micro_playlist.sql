-- This file defines the schema for a test database.

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

    INSERT INTO tracks(title, album, artist, len, track_url, art_url) VALUES("Who Dat Boy", "Flower Boy", "Tyler, The Creator", "3:25", '0', '0');
    INSERT INTO tracks(title, album, artist, len, track_url, art_url) VALUES("Yonkers", "Goblin", "Tyler, The Creator", "4:11", '0', '0');
    INSERT INTO tracks(title, album, artist, len, track_url, art_url) VALUES("I Ain't Got Time", "Flower Boy", "Tyler, The Creator", "3:26", '0', '0');
    INSERT INTO tracks(title, album, artist, len, track_url, art_url) VALUES("The Execution of All Things", "The Execution of All Things", "Rilo Kiley", "4:13", '0', '0');
    INSERT INTO tracks(title, album, artist, len, track_url, art_url) VALUES("My Slumbering Heart", "The Execution of All Things", "Rilo Kiley", "5:36", '0', '0');
    COMMIT;
