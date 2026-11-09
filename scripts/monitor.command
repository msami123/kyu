#!/bin/zsh
cd -- "${0:A:h:h}" || exit 1
printf '\033]0;KYU - Live Agent Monitor\007\033[8;42;150t\033[2J\033[H'
exec /usr/bin/python3 scripts/monitor.py --watch
