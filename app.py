from flask import Flask, render_template
from flask_socketio import SocketIO
from exchange_api.main_api import ExchangeApi

app = Flask(__name__)
socketio = SocketIO(app)
exchange = ExchangeApi()


@socketio.on('click')
def handle_message(msg):
    """
    Handle a click event from the client and emit the response with the exchange rate information.

    Parameters:
    - msg: The message object containing date, base currency, base amount, and counter currency.

    Return Type: None
    """
    # read parameters
    date = msg['date']
    base_currency = msg['baseCcy']
    base_amount = msg['baseAmt']
    counter_currency = msg['counterCcy']
    error_msg, success_msg = None, None

    # get exchange rate
    exchange_rate = exchange.convert(base_currency, counter_currency, base_amount, date)

    # handle response
    if 'error' in exchange_rate:
        error_msg = exchange_rate['error']
        answer = None
    else:
        success_msg = f'As of {date}, {base_amount} {base_currency} is equivalent to {exchange_rate["converted_amount"]} {counter_currency}.'
        answer = exchange_rate["converted_amount"]

    response = {
        'msg': error_msg if 'error' in exchange_rate else success_msg,
        'error': 'error' in exchange_rate,
        'answer': answer
    }

    # emit response
    socketio.emit('rate', response)


@app.route('/')
def main():
    """
    Main route handler.
    Retrieves assets from the exchange cache and generates HTML options for the assets.
    Returns:
        str: Rendered HTML content with assets as options.
    """
    # create dropdown options
    assets = exchange.cache[max(exchange.cache.keys())]['usd'].keys()
    pairs = ''.join([f'<option value="{a}">{a}</option>' for a in assets])
    return render_template('content.html', assets=pairs)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', allow_unsafe_werkzeug=True)
