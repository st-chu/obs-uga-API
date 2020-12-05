from flask import Flask, render_template, request
import requests
import csv


response = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
data = response.json()
date = data[0]['effectiveDate']
exchange = data[0]['rates']

with open('exchange_rate.csv', 'w') as exchange_rate_csv:
    fieldnames = ['currency', 'code', 'bid', 'ask']
    csv_writer = csv.DictWriter(exchange_rate_csv, fieldnames=fieldnames, delimiter=';')
    csv_writer.writeheader()
    for item in exchange:
        csv_writer.writerow(item)

for item in exchange:
    item['ask'] = round(item['ask'], 4)
    item['bid'] = round(item['bid'], 4)


def multiplier(items, operation, code):
    for _item in items:
        print(_item)
        if _item['code'] == code:
            mult = _item[operation]
            return float(mult)


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
            bid = multiplier(exchange, operation, code)
            score = round(amount / bid, 2)
            amount_str = '{:.2f}'.format(amount)
            return render_template(
                'exchange.html',
                items=exchange,
                operation=operation,
                amount=amount_str,
                score=score,
                code=code,
                date=date,
                bid=round(float(bid), 2)
            )
        elif operation == 'ask':
            ask = multiplier(exchange, operation, code)
            score = round(amount * ask, 2)
            amount_str = '{:.2f}'.format(amount)
            return render_template(
                'exchange.html',
                items=exchange,
                operation=operation,
                amount=amount_str,
                score=score,
                code=code,
                date=date,
                ask=round(float(ask), 2)
            )
