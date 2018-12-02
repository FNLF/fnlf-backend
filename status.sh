#!/bin/bash

if [ -f /home/haakon/server/dev/fnlf-backend/gunicorn.pid ];then
        echo "FNLF-BACKEND is running"
else
        echo "NOT RUNNNING!"
fi
