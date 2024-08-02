#!/bin/sh

cd /database
python3 createdb.py
python3 fillDB.py
#python3 generate_testdata.py
cd /

while [ true ]; do
 cd /API
 uvicorn main:app --host 0.0.0.0 --reload --ssl-keyfile=/ssl/keyfile.pem --ssl-certfile=/ssl/certfile.pem
 sleep 10
done

