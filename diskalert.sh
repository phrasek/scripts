#!/bin/sh

message=$(df -H | grep /dev/vda1 | awk -v ALERT="90" '$5 >= ALERT {printf "/dev/vda1 is almost full:%d%", $5}')
if [ -n "$message" ]; then
  echo "$message" | mail -s "Alert: Almost out of disk space" email
fi