#!/bin/zsh

# LOC="`dirname \"$0\"`"
LOC=`pwd`
notify-send --urgency=normal --icon=$LOC/icon.png $1 $2
if [[ $3 == 'start' ]]; then
  paplay sounds/start.wav &
else
  paplay sounds/stop.wav &
fi
