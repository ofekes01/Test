#!/bin/bash

if [ "$(ps -ef| grep f5_backup.py | grep -v grep |wc -l)" ] ; then
    exit 0
else
    exit 1
fi
