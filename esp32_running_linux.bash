#!/bin/sh
SERVICE='esp32_code.py'

if ps ax | grep -v grep | grep $SERVICE > /dev/null
then
    echo "$SERVICE service running, everything is fine" > /dev/null #sin mensaje
else
    echo "$SERVICE is not running. Starting."
    /path/to/$SERVICE &
fi