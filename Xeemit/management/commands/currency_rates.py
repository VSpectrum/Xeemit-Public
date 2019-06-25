# script to run once every day
import requests, lxml
from django.utils import timezone
from bs4 import BeautifulSoup
from decimal import Decimal
from django.core.management import BaseCommand
from Xeemit.models import CurrencyData


class Command(BaseCommand):
    help = "This gathers data on mid-market rates for currencies and updates table with latest rates from www.xe.com"

    def handle(self, *args, **options):
        currency_list = ["AED","AFN","ALL","AMD","ANG","AOA","ARS","AUD","AWG","AZN","BAM","BBD","BDT","BGN","BHD","BIF","BMD","BND","BOB","BRL","BSD","BTN","BWP","BYN","BZD","CAD","CDF","CHF","CLP","CNY","COP","CRC","CUC","CUP","CVE","CZK","DJF","DKK","DOP","DZD","EGP","ERN","ETB","EUR","FJD","FKP","GBP","GEL","GGP","GHS","GIP","GMD","GNF","GTQ","GYD","HKD","HNL","HRK","HTG","HUF","IDR","ILS","IMP","INR","IQD","IRR","ISK","JEP","JMD","JOD","JPY","KES","KGS","KHR","KMF","KPW","KRW","KWD","KYD","KZT","LAK","LBP","LKR","LRD","LSL","LYD","MAD","MDL","MGA","MKD","MMK","MNT","MOP","MRO","MUR","MVR","MWK","MXN","MYR","MZN","NAD","NGN","NIO","NOK","NPR","NZD","OMR","PAB","PEN","PGK","PHP","PKR","PLN","PYG","QAR","RON","RSD","RUB","RWF","SAR","SBD","SCR","SDG","SEK","SGD","SHP","SLL","SOS","SPL*","SRD","STD","SVC","SYP","SZL","THB","TJS","TMT","TND","TOP","TRY","TTD","TVD","TWD","TZS","UAH","UGX","USD","UYU","UZS","VEF","VND","VUV","WST","XAF","XCD","XDR","XOF","XPF","YER","ZAR","ZMW","ZWD"]

        for currency_code in currency_list:
            try:
                today = timezone.now()
                response = requests.get('http://www.xe.com/currencyconverter/convert/?Amount=1&From=USD&To='+currency_code)
                if response.status_code==200:
                    soup = BeautifulSoup(response.text, "lxml")
                    curr_value = soup.find('span', {'class': 'uccResultAmount'})
                    if curr_value:
                        obj, created = CurrencyData.objects.get_or_create(currency_code=currency_code)
                        obj.currency_rate = Decimal(curr_value.text.replace(',', ''))
                        obj.dateUpdated = today
                        obj.save()

            except:
                with open("error.log", 'a+') as f:
                    f.write(str(timezone.now())+"  ---  Error occurred when doing: "+currency_code)