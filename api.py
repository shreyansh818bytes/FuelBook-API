import flask
from flask import request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = flask.Flask(__name__)
app.config['DEBUG'] = True


# Scrape the data
def get_data(url):
    r = requests.get(url)
    html_data = r.text
    soup = BeautifulSoup(html_data, 'html.parser')

    result_date_block = soup.find_all("div", class_="fuel-block-date")
    result_date_block = re.findall(".\d+\.\d+", str(result_date_block))
    result_date_block = [x if x[0] == '-' else x[1:] for x in result_date_block]

    result_details_block = soup.find_all("div", class_="fuel-block-details")
    result_details_block = re.findall(".\d+\.\d+", str(result_details_block))
    result_details_block = [x if x[0] == '-' else x[1:] for x in result_details_block]

    result_json = dict()
    if len(result_date_block):
        result_json['price_change'] = float(result_date_block[0])
        result_json['price_current'] = float(result_details_block[0])
    else:
        result_json['price_current'] = float(result_details_block[0])
        if len(result_details_block) == 2:
            result_json['price_change'] = float(result_details_block[1])
        else:
            result_json['price_change'] = float(0)

    return result_json


@app.route('/', methods=['GET'])
def home():
    return '''<h1>FuelBook API</h1>
    <p><h3>This api is created for FuelBook Android App project to scrape fuel price data district wise.<br> 
    Support for Indian cities only</h3>
    <b>Developer's Instructions:</b><br>
    &emsp;&emsp;* API is at /api/v1/fuelprice<br>
    &emsp;&emsp;* Parameters required : fType (Type of fuel [petrol, diesel, lpg])<br>
    &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;district (Name of the District)<br>
    &emsp;&emsp;* Return Example: {<br>
    &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;price_current: 89.01,<br>
    &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;price_change: -0.20<br>
    &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;}<br><br>
    <br>
    Android App: Under Development...<br>
    Contact Developer: <a href='mailto:shr818bytes@gmail.com'>shr818bytes@gmail.com</a></p>
    <br><br><br>
    <h5>Data Source: <a href='https://www.goodreturns.in/'>goodreturns Website</a></h5>'''


@app.route('/api/v1/fuelprice', methods=['GET'])
def return_data():
    if 'fType' in request.args and 'district' in request.args:
        fuel_type = request.args['fType']
        district_name = request.args['district']
        try:
            response = get_data(f"https://www.goodreturns.in/{fuel_type}-price-in-{district_name}.html")
        except IndexError:
            response = {
                "error": {
                    "Data Not Found": request.args
                }
            }
        return jsonify(response)
    error_details = {
        "error": {
            "Invalid Parameter Key": request.args
        }
    }
    return jsonify(error_details)


@app.errorhandler(500)
def internal_error(e):
    return '''<h1>Internal Error: 500</h1>
    <p>''' + e + '''</p>
    <h3>Please post the error logs to Developer's Email (shr818bytes@gmail.com)</h3>'''


@app.errorhandler(404)
def page_not_found(e):
    return '''<h1>Page not found: 404</h1>
    <p>Can't find what you are looking for.</p>'''


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
