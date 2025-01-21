from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

API_KEY = '7e234eeeeaeef440d8eb7f2fdff8702d'  

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/weather')
def weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if lat and lon:
        url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
        response = requests.get(url)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Unable to fetch weather data', 'message': response.json().get('message', 'Unknown error')})
    return jsonify({'error': 'Location not provided'})

if __name__ == '__main__':
    app.run(debug=True)
