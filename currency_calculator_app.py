from flask import Flask, render_template, request
import requests
import csv
from typing import Dict, Union
import pickle


# creating a Currency class
class Currency:
    def __init__(self, currency: str, code: str, bid: str, ask: float) -> None:
        self.currency = currency
        self.code = code
        self.bid = bid
        self.ask = ask

    def __str__(self) -> str:
        return f'Waluta: {self.currency}({self.code})\nKupno: {self.ask} PLN\nSprzedaż: {self.bid} PLN'


# download data from the API of the NBP
response = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
data = response.json()
date = data[0]['effectiveDate']
exchange = data[0]['rates']

# creating an instance of the Currency class
dolar = Currency(
    currency=exchange[0]['currency'],
    code=exchange[0]['code'],
    bid=exchange[0]['bid'],
    ask=exchange[0]['ask']
)
euro = Currency(
    currency=exchange[3]['currency'],
    code=exchange[3]['code'],
    bid=exchange[3]['bid'],
    ask=exchange[3]['ask']
)
forint = Currency(
    currency=exchange[4]['currency'],
    code=exchange[4]['code'],
    bid=exchange[4]['bid'],
    ask=exchange[4]['ask']
)

# pickling lists with instances of Currency clacy
lista = [euro, dolar, forint]
with open("exchange_rate.pickle", 'wb') as exchange_rate_pickle:
    pickle.dump(lista, exchange_rate_pickle)
with open("exchange_rate.pickle", 'rb') as exchange_rate_pickle:
    lista2 = pickle.load(exchange_rate_pickle)


# saving data to csv file
with open('exchange_rate.csv', 'w') as exchange_rate_csv:
    fieldnames = ['currency', 'code', 'bid', 'ask']
    csv_writer = csv.DictWriter(exchange_rate_csv, fieldnames=fieldnames, delimiter=';')
    csv_writer.writeheader()
    for item in exchange:
        csv_writer.writerow(item)

# round the ask and bid values to four decimal places
for item in exchange:
    item['ask'] = round(item['ask'], 4)
    item['bid'] = round(item['bid'], 4)

exchange_dic = {}
for item in exchange:
    exchange_dic.setdefault(item['code'], {'bid': item['bid'], 'ask': item['ask'], 'currency': item['currency']})


def multiplier(items: Dict[str, Dict[str, Union[str, float]]], operation: str, code: str) -> float:
    return items.get(code).get(operation)


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'GET':
        return render_template('exchange.html', items=exchange)
    elif request.method == 'POST':
        form_data = request.form
        code = form_data.get('code')
        operation = form_data.get('operation')
        amount = form_data.get('amount')
        if bool(amount) is True:
            try:
                amount = amount.replace(',', '.')
                amount = float(amount)
            except ValueError:
                operation = 'notNumber'
                return render_template(
                    'exchange.html',
                    items=exchange,
                    operation=operation,
                    amount=amount
                )
        if all([bool(code), bool(operation), bool(amount)]) is False:
            operation = 'noValue'
            return render_template('exchange.html', items=exchange, operation=operation)
        if operation == 'bid':
            bid = multiplier(exchange_dic, operation, code)
            score = round(amount / bid, 2)
            score_str = '{:.2f}'.format(score)
            amount_str = '{:.2f}'.format(amount)
            bid = round(bid, 2)
            bid_str = '{:.2f}'.format(bid)
            print(f"Request: code = {code}, operation = {operation}, amount = {amount}PLN ")
            print(f"Response: score = {score}{code}")
            return render_template(
                'exchange.html',
                items=exchange,
                operation=operation,
                amount=amount_str,
                score=score_str,
                code=code,
                date=date,
                bid=bid_str
            )
        elif operation == 'ask':
            ask = multiplier(exchange, operation, code)
            score = round(amount * ask, 2)
            score_str = '{:.2f}'.format(score)
            amount_str = '{:.2f}'.format(amount)
            ask = round(ask, 2)
            ask_str = '{:.2f}'.format(ask)
            print(f"Request: code = {code}, operation = {operation}, amount = {amount}{code}")
            print(f"Response: score = {score}PLN")
            return render_template(
                'exchange.html',
                items=exchange,
                operation=operation,
                amount=amount_str,
                score=score_str,
                code=code,
                date=date,
                ask=ask_str
            )
