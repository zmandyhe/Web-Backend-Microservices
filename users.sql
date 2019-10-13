-- $ sqlite3 books.db < sqlite.sql

PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER primary key,
    username VARCHAR,
    userpassword VARCHAR,
    displayname VARCHAR,       
    email VARCHAR,
    homepageurl VARCHAR
    UNIQUE(published, author, title)
);
INSERT INTO users(username, userpassword, displayname, email,homepageurl) VALUES('Ann Leckie','goodluck', 'Ann','al@gmail.com','http://www.ann.com');
COMMIT;
