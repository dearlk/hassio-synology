#!/bin/bash
set -e
HOST=192.168.1.44
USER=dearlk

cd /backup
echo "Backing up snapshot files from /backup directory..."
scp -p *.tar  $USER@$HOST:hassio_snapshots
echo "finished, now deleting files from /backup directory..."
rm *.tar
echo "finished"




