import random
from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from itertools import groupby
import json 
import sqlite3
import io
import csv

app = Flask(__name__)

# Database connection details
db_config = {
    'host': 'localhost',
    'user': 'sqluser',
    'password': 'password',
    'database': 'store'
}

def get_data_from_db():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Successfully connected to the database")
            # Query to get all the data needed for the report
            query = """
                SELECT s.store_id, s.timestamp_utc, s.status, h.day_of_week, h.start_time_local, h.end_time_local
                FROM store_status s
                LEFT JOIN store_hours h ON s.store_id = h.store_id
                ORDER BY s.store_id, s.timestamp_utc
            """
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            data = cursor.fetchall()
            connection.close()
            return data
    except Error as e:
        print("Error while connecting to the database", e)
        return None

def calculate_uptime_downtime(data):
    # Calculate uptime and downtime based on business hours
    report = []
    for store_id, entries in groupby(data, key=lambda x: x['store_id']):
        entries = list(entries)
        business_hours = {
            day: (datetime.strptime(start_time, '%H:%M:%S'), datetime.strptime(end_time, '%H:%M:%S'))
            for day, start_time, end_time in set((entry['day_of_week'], entry['start_time_local'], entry['end_time_local']) for entry in entries if entry['day_of_week'] is not None)
        }

        # Generate timestamps for business hours
        timestamps = []
        for day, (start_time, end_time) in business_hours.items():
            timestamp = start_time
            while timestamp <= end_time:
                timestamps.append({'store_id': store_id, 'timestamp_utc': timestamp, 'status': 'unknown'})
                timestamp += timedelta(hours=1)

        # Populate statuses based on the data
        for entry in entries:
            timestamp = entry['timestamp_utc']
            for ts in timestamps:
                if ts['timestamp_utc'] == timestamp:
                    ts['status'] = entry['status']

        # Calculate uptime and downtime
        uptime = 0
        downtime = 0
        last_status = None
        for ts in timestamps:
            if ts['status'] == 'active':
                uptime += 1
                if last_status == 'inactive':
                    downtime -= 1
            elif ts['status'] == 'inactive':
                downtime += 1
                if last_status == 'active':
                    uptime -= 1
            last_status = ts['status']

        uptime_last_hour = uptime
        uptime_last_day = uptime
        uptime_last_week = uptime

        downtime_last_hour = downtime
        downtime_last_day = downtime
        downtime_last_week = downtime

        report.append({
            'store_id': store_id,
            'uptime_last_hour': uptime_last_hour,
            'uptime_last_day': uptime_last_day,
            'uptime_last_week': uptime_last_week,
            'downtime_last_hour': downtime_last_hour,
            'downtime_last_day': downtime_last_day,
            'downtime_last_week': downtime_last_week
        })

    return report

def create_report_table():
    # Create a connection to the SQLite database
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()

    # Create a table for reports if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            report_id INTEGER PRIMARY KEY,
            report_data TEXT
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def save_report_to_db(report):
    # Create a connection to the SQLite database
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()

    # Convert the report to a JSON string
    report_json = json.dumps(report)

    # Insert the report data into the database
    cursor.execute('INSERT INTO reports (report_data) VALUES (?)', (report_json,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def fetch_report_from_db(report_id):
    # Create a connection to the SQLite database
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()

    # Fetch the report data from the database
    cursor.execute('SELECT report_data FROM reports WHERE report_id = ?', (report_id,))
    row = cursor.fetchone()

    # Close the connection
    conn.close()

    if row is not None:
        # Convert the JSON string back to a list of dictionaries
        report_data = json.loads(row[0])
        return report_data
    else:
        return None

def convert_to_csv(report):
    # Create a StringIO object to store CSV data
    csv_data = io.StringIO()
    # Define CSV header
    header = ['store_id', 'uptime_last_hour', 'uptime_last_day', 'uptime_last_week', 'downtime_last_hour', 'downtime_last_day', 'downtime_last_week']

    # Write data to CSV
    writer = csv.DictWriter(csv_data, fieldnames=header)
    writer.writeheader()
    for row in report:
        writer.writerow(row)

    # Reset the StringIO position to the beginning
    csv_data.seek(0)
    return csv_data

@app.route('/trigger_report', methods=['GET'])
def trigger_report():
    data = get_data_from_db()
    if data is None:
        return jsonify({'message': 'Error occurred while fetching data from the database'}), 500

    report = calculate_uptime_downtime(data)

    # Generate a random report_id (you can use any method to generate unique IDs)
    report_id = random.randint(1000, 9999)

    # Store the report in the 'results' table
    save_report_to_db(report)

    return jsonify({'report_id': report_id})

@app.route('/get_report', methods=['GET'])
def fetch_report():
    report_id = request.args.get('report_id')
    if report_id is None:
        return jsonify({'message': 'Missing report_id in the request'}), 400

    # Fetch the report from the 'results' table
    report = fetch_report_from_db(report_id)

    if report is None:
        return jsonify({'message': 'Invalid report_id or report generation is still running'}), 404

    return jsonify({'report': report})
if __name__ == '__main__':
    create_report_table()

    app.run(debug=True)
