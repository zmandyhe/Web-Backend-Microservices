#!/bin/bash
# This is a small script to create the schema for a fresh database.

sqlite3 ../../../var/micro_playlist.db < ./new_micro_playlist.sql

