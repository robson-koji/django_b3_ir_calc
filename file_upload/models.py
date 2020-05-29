# coding: utf-8

import os
import time

from django.db import models
from django.contrib.auth.models import User
from stock_price.models import StockPrice
from stock_price.stock_price import get_stocks, get_price



def get_upload_path(instance, filename):
    today  = time.strftime('%Y/%m/%d')
    (file, session) = filename.split('|')
    return os.path.join('documents', session, today, file)

class Document(models.Model):
    #docfile = models.FileField(upload_to='documents/%Y/%m/%d')
    docfile = models.FileField(upload_to=get_upload_path)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    session_key = models.CharField(max_length=40)




from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from datetime import datetime, date, timedelta

import csv

from b3_ir_calc.b3_ir_calc.b3excel2csv import excel_to_csv


"""
def get_stocks(filename, stocks):

    def hasNumbers(inputString):
        return any(char.isdigit() for char in inputString)

    # stocks = set()
    with open(filename) as file_handler:
        csv_reader = csv.reader(file_handler, quotechar='"', delimiter=',')

        print(filename)
        for line in csv_reader:
            # print(line)
            if '.' in line[4] or 'null' in line[4]:
                continue

            if not hasNumbers(line[4]):
                continue

            stocks.add(line[4].split()[0])
    # return stocks
"""



# method for updating
@receiver(post_save, sender=Document)
def update_stock_price(sender, instance, **kwargs):

    # Para testar sem ter que atualizar sempre.
    today = date.today() - timedelta(days=4)
    file = instance.docfile.name

    # Excel 2 CSV conversion
    excel_to_csv(path=None, file=file)

    csv_path = "%s%s" % (settings.MEDIA_ROOT, file)
    csv_path = csv_path.replace('.xls', '.csv')
    stocks = set()

    # Get stocks from csv
    get_stocks(csv_path, stocks)

    # Check stock exists and update price.
    for stock in stocks:
        stock_obj, created = StockPrice.objects.get_or_create(
            stock=stock
        )

        # Get stock price
        if not stock_obj.last_update or stock_obj.last_update.date() < today:
            (price, hour) = get_price(stock_obj.stock)
            stock_obj.price = price
            stock_obj.hour = hour
            stock_obj.last_update = datetime.now()
            stock_obj.save()
            # import pdb; pdb.set_trace()
        else:
            print("Atualizado: %s" % (stock_obj.stock))
