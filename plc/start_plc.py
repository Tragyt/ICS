import time
from dotenv import load_dotenv
import os

import requests
from bs4 import BeautifulSoup

load_dotenv() 
s = requests.Session()

soup = BeautifulSoup(s.get("http://localhost:8080/login").text, "html.parser")
csrf = soup.find("input", {"name": "csrf_token"})["value"]
login = {"username": os.getenv("OPENPLC_ADMIIN"), "password": os.getenv("OPENPLC_PASSWORD"), "csrf_token": csrf}

s.post("http://localhost:8080/login", data=login)
s.get("http://localhost:8080/compile-program?file=arm_plc.st")

time.sleep(10)
s.get("http://localhost:8080/start_plc")
