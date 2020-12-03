from flask import Flask
import requests
import csv


response = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
data = response.json()
exchange = data[0]['rates']
with open('exchange_rate.csv', 'w') as exchange_rate_csv:
    fieldnames = ['currency', 'code', 'bid', 'ask']
    csv_writer = csv.DictWriter(exchange_rate_csv, fieldnames=fieldnames, delimiter=';')
    csv_writer.writeheader()
    for item in exchange:
        csv_writer.writerow(item)
print(exchange)