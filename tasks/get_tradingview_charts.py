import urllib, datetime
from selenium import webdriver
from time import sleep
from PIL import Image


import os, django
from django.conf import settings
from django_b3_ir_calc import settings as myapp_defaults
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_b3_ir_calc.settings')
django.setup()
from stock_price.models import StockPrice


"""
First of all, install geckodriver:
https://askubuntu.com/questions/851401/where-to-find-geckodriver-needed-by-selenium-python-package
https://github.com/mozilla/geckodriver/releases/tag/v0.29.0

* copy profile
* Install XVFB
https://dzone.com/articles/taking-browser-screenshots-no
"""


stocks = StockPrice.objects.all()

images_dir = myapp_defaults.MEDIA_ROOT + 'tradingview_charts/'

def screenshot_tradingview(stock):
    fp = webdriver.FirefoxProfile('/home/robson/.mozilla/firefox/mbinghgc.selenium_tradingview')

    browser = webdriver.Firefox(fp)

    browser.set_window_position(0, 0)
    browser.set_window_size(1024, 576)

    #browser.get("https://br.tradingview.com/chart?symbol=BMFBOVESPA%3AB3SA3")
    # import pdb; pdb.set_trace()
    url = "https://br.tradingview.com/chart?symbol=BMFBOVESPA:%s" % (stock.stock)
    img_name = "%s%s.png" % (images_dir, stock.stock)
    browser.get(url)
    # browser.get("https://www.lambdatest.com/feature")
    sleep(10)
    featureElement=browser.find_element_by_class_name('layout__area--center').screenshot(img_name)
    browser.quit()


for stock in stocks:
    screenshot_tradingview(stock)
    sleep(150)
