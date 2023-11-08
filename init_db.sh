#!/bin/bash

source .env

create_database_and_run_script() {
    createdb -U $DB_USER $DB_NAME
    if [ $? -eq 0 ]; then
        echo "New database created successfully."
        psql -U $DB_USER -d $DB_NAME -a -v DB_NAME="$DB_NAME" -f $SQL_SCRIPT
    else
        echo "Failed to create a new database."
    fi
}

if psql -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo "Dropping existing database $DB_NAME"
    dropdb -U $DB_USER $DB_NAME
    if [ $? -eq 0 ]; then
        echo "Database dropped successfully."
        create_database_and_run_script
    else
        echo "Failed to drop the existing database. Try again."
    fi
else
    echo "Database $DB_NAME doesn't exist. Creating a new one."
    create_database_and_run_script
fi
