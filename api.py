import flask
from flask import request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = flask.Flask(__name__)
app.config['DEBUG'] = False


# Scrape the data
def get_data(url, district_name, fuel_type):
    r = requests.get(url)
    html_data = r.text
    soup = BeautifulSoup(html_data, 'html.parser')

    result_table = soup.find_all("div", class_="tbl-container b_rad4 overflow-hidden")
    result_table = result_table[0].find_all("tr")

    result_items = []
    for item in result_table[1:]:
        row_items = item.find_all('td')
        row_items[0] = re.findall('">.*.</a', str(row_items[0]))[0][2:-3]
        row_items[0] = row_items[0].lower().replace(' ', '-')
        if district_name in row_items[0]:
            row_items[1] = [float(re.findall(">.*. ", str(row_items[1]))[0][1:-1]),
                            re.findall(" .*.<", str(row_items[1]))[0][1:-1].replace('₹', 'Rs')]
            row_items.append(re.findall('up|down', str(row_items[2]))[0])
            row_items[2] = float(re.findall('">.*.</s', str(row_items[2]))[0][2:-3])
            if row_items[3] == 'up' and row_items[2]:
                row_items[2] = -row_items[2]
            row_items = row_items[:-1]
            result_items.append(row_items)

    result_items = result_items[0]

    result_json = {
        'district': result_items[0],
        'price_current': {
            'value': result_items[1][0],
            'unit': result_items[1][1]
        },
        'price_change': result_items[2],
        'fuel_type': fuel_type
    }

    return result_json


@app.route('/', methods=['GET'])
def home():
    return '''<h1>FuelBook API</h1>
    <p><h3>This api is created for FuelBook Android App project to scrape fuel price data district wise.<br> 
    Support for Indian cities only</h3>
    <b>Developer's Instructions:</b><br>
    &emsp;&emsp;* API is at /api/fuel-price/city<br>
    &emsp;&emsp;* Parameters required : fType (Type of fuel [petrol, diesel])<br>
    &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;district (Name of the District)<br>
    &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;state (Name of the State)<br>
    &emsp;&emsp;* API Request Example: <a 
    href='https://fuelbook-api.herokuapp.com/api/fuel-price/city?fType=petrol&state=maharashtra&district=greater-mumbai'>
        /api/fuel-price/city?fType=petrol&state=maharashtra&district=greater-mumbai
    </a>
    <br>
    <br>
    <br>
    Android App: Under Development...<br>
    Contact Developer: <a href='mailto:shr818bytes@gmail.com'>shr818bytes@gmail.com</a></p>
    <br><br><br>
    <h5>Data Source: <a href='https://www.ndtv.com/'>NDTV Website</a></h5>'''


@app.route('/api/fuel-price/city', methods=['GET'])
def return_data():
    if 'fType' in request.args and 'district' in request.args and 'state' in request.args:
        fuel_type = request.args['fType']
        district_name = request.args['district'].lower().replace(' ', '-')
        state_name = request.args['state']
        try:
            response = get_data(f"https://www.ndtv.com/fuel-prices/{fuel_type}-price-in-{state_name}-state",
                                district_name,
                                fuel_type)
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
