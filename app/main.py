import os

# change the working directory to the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

import time
import schedule
import protobot

import applog



applog.info("Started scheduling")
    
schedule.every(24).hours.do(protobot.update)

while True:
    try:
        schedule.run_pending()
        time.sleep(60)
    except Exception as e:
        applog.error(e)
