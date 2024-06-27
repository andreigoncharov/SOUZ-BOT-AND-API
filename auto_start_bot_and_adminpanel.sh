#!/bin/bash
source /env/bin/activate
cd /SOUZ-BOT-AND-API/api/
gunicorn --bind 0.0.0.0:8000 api.wsgi --workers=5 --threads 10 --daemon
cd /SOUZ-BOT-AND-API
nohup python3.9 bot.py &
