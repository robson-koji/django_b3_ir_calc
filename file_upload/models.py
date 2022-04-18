# coding: utf-8

from datetime import datetime, date, timedelta
import os, csv, time

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from b3_ir_calc.b3_ir_calc.b3excel2csv import excel_to_csv
from data_source.views import get_stocks_from_user_file
from stock_price.stock_price import get_price
from stock_price.models import StockPrice


def get_upload_path(instance, filename):
    today  = time.strftime('%Y/%m/%d')
    (file, session) = filename.split('|')
    return os.path.join('documents', session, today, file)


class Document(models.Model):
    """ CSV file uploaded by user (b3 CEI file) """
    docfile = models.FileField(upload_to=get_upload_path)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    session_key = models.CharField(max_length=40)


@receiver(post_save, sender=Document)
def update_stock_price(sender, instance, **kwargs):
    """
    Signal - After save document (csv file uploaded by user),
    create or update stock price
    """
    # If file is trail, dont update stock prices.
    if 'trial_cei_file.csv' in instance.docfile.name:
        return

    # If merged file... Does not update if someone uploads a "merged" on filename.
    if '_merged_' in  instance.docfile.name:
        return


    # Para testar sem ter que atualizar sempre.
    today = date.today() - timedelta(days=4)
    file = instance.docfile.name
    if not '.csv' in file:        
        # Excel 2 CSV conversion
        excel_to_csv(path=None, file=file)

        csv_path = "%s%s" % (settings.MEDIA_ROOT, file)
        csv_path = csv_path.replace('.xls', '.csv')
    else:
        csv_path = "%s%s" % (settings.MEDIA_ROOT, file)
        
    stocks = set()

    # Get stocks from csv
    get_stocks_from_user_file(csv_path, stocks)

    # Check stock exists and utodaypdate price.
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
