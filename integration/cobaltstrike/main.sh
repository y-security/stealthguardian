#!/bin/sh
ln -s /cobaltstrike/watcher.py /root/watcher.py



while :; do
  echo "Started Cobalt Strike Watcher"
  python3 -u /root/watcher.py
  echo "Cobalt Strike Watcher terminated ... Restarting"
  sleep 1
done