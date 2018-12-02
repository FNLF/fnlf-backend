#!/bin/bash

INVENV=$(python -c 'import sys; print ("1" if hasattr(sys, "real_prefix") else "0")')

cd /home/haakon/server/dev/fnlf-backend

if [[ INVENV == 0 ]]
then
        source bin/acticate
fi

gunicorn -w 5 -b localhost:8081 run:app --log-level=debug --log-file=unicorn.log --pid gunicorn.pid --capture-output --enable-stdio-inheritance &

if [[ INVENV == 0 ]]
then
        deactivate
fi

cd
