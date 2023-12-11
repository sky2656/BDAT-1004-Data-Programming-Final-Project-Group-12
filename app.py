# app.py

from flask import Flask, render_template, jsonify,request
import requests
from pymongo import MongoClient
import time
import schedule

app = Flask(__name__)
username = quote_plus('rahulbaldaniyatech2013')
password = quote_plus('rb@123456789')
cluster = 'rbaldaniya.4dxjsmi.mongodb.net'

uri = 'mongodb+srv://' + username + ':' + password + '@' + cluster +"/?retryWrites=true&w=majority"

def fetch_and_store_data():
    url = "https://raw.githubusercontent.com/justmarkham/DAT8/master/data/u.user"
    response = requests.get(url)
    data = response.text.split('\n')[1:]

    # MongoDB connection
    client = MongoClient(uri)
    db = client["ritviz"]
    collection = db["assign"]

    # Iterate through data and insert into MongoDB
    for line in data:
        if line:
            fields = line.split('|')
            user_data = {
                "user_id": int(fields[0]),
                "age": int(fields[1]),
                "gender": fields[2],
                "occupation": fields[3],
                "zip_code": fields[4]
            }
            collection.insert_one(user_data)

# Route to trigger data acquisition
@app.route('/acquire-data')
def acquire_data():
    fetch_and_store_data()
    return 'Data acquisition successful!'

# Route to display data on a web page
@app.route('/')
def display_data():
    client = MongoClient()
    db = client["ritviz"]
    collection = db["assign"]
    # Retrieve data from MongoDB
    data = list(collection.find())

    # Render HTML template with data
    return render_template('index.html', data=data)

@app.route('/api/data/<int:user_id>', methods=['GET'])
def api_get_item_by_id(user_id):
    client = MongoClient(uri)
    db = client["ritviz"]
    collection = db["assign"]
    data = collection.find_one({'user_id': user_id}, {'_id': 0})
    if data:
        # Return data as JSON
        return jsonify(data)
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/api/data/range', methods=['GET'])
def api_get_range_items():
    start_age = int(request.args.get('start_age', 0))
    end_age = int(request.args.get('end_age', 100))

    client = MongoClient(uri)
    db = client["ritviz"]
    collection = db["assign"]

    # Retrieve data within the specified age range
    data = list(collection.find({'age': {'$gte': start_age, '$lte': end_age}}, {'_id': 0}))

    # Return data as JSON
    return jsonify(data)

@app.route('/api/data', methods=['GET'])
def api_data():
    client = MongoClient(uri)
    db = client["ritviz"]
    collection = db["assign"]

    data = list(collection.find({}, {'_id': 0}))

    # Return data as JSON
    return jsonify(data)

def periodic_data_acquisition():
    fetch_and_store_data()

# Schedule data acquisition every 24 hours
schedule.every(24).hours.do(periodic_data_acquisition)

if __name__ == '__main__':
    app.run(debug=True,port=4000)
     # Run the scheduled tasks in the background
    while True:
        schedule.run_pending()
        time.sleep(1)
