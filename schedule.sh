#!/bin/zsh

if [ -n `pgrep atd` ]; then
  echo atd running
else
  sudo systemctl start atd && echo started atd
fi




