#!/bin/bash

if [ ! -f /home/haakon/server/dev/fnlf-backend/gunicorn.pid ];then
        echo "No pid file, exiting"
else
        kill -15 `cat /home/haakon/server/dev/fnlf-backend/gunicorn.pid`
        echo "Killed process from pid file"
        # Should wait and recheck and if still pid, then kill -9
fi

if [ -f /home/haakon/server/dev/fnlf-backend/melwin_updater.pid ];then
        rm /home/haakon/server/dev/fnlf-backend/melwin_updater.pid
fi
