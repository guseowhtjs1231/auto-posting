import os
import django
import sys
from datetime import timedelta
import datetime

from bs4 import BeautifulSoup
import requests
import re
import csv
import time
from selenium import webdriver
from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog_project.settings")
django.setup()

from blog.models import *

CSV_PATH_PRODUCTS = '/Users/youngbinha/Desktop/blogproject/question_url_info75000.csv'

with open(CSV_PATH_PRODUCTS) as in_file:
    data_reader = csv.reader(in_file)
    next(data_reader,None)
    for row in data_reader:
        row_data    = row[0].strip('{').strip('}').split(', ')
        for i in row_data:
            end_point = i.strip("'")
            Question.objects.create(question_endpoint=end_point)
            print(end_point)
        