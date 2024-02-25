#!/bin/bash
FILENAME="$1"
# The rest of your script can use $FILENAME as the variable holding the passed filename

# import username and password etc from .env file
source .env

# upload to mongodb

mongoimport --uri "mongodb+srv://$USERNAME:$PASSWORD@pawnalyze.cmmknar.mongodb.net/?retryWrites=true&w=majority&appName=Pawnalyze" \
    --collection $COLLECITON \
    --file $FILENAME \
    --db $DB \
    --jsonArray
