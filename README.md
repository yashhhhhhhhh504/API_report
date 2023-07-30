# API_report
This repository contains a Flask application for generating and fetching store status reports based on data from the "store_status," "store_hours," and "store_timezone" tables in the "store" database.

# Requirements
Before running the application, make sure you have the following installed:

Python 3.x
Flask
MySQL Connector
SQLite (for creating a local SQLite database)
Setup
Create the "store" database in your MySQL server and run the provided SQL statements to create the necessary tables: "store_status," "store_hours," and "store_timezone."

Install the required Python packages using pip:

      pip install Flask mysql-connector-python

Clone this repository to your local machine.
Modify the db_config dictionary in the Flask application (app.py) with your MySQL database connection details.
Ensure that you have read and write access to the directory where the Flask application is located.
Optionally, create a virtual environment for the application:


python -m venv venv
source venv/bin/activate  # On Windows, use "venv\Scripts\activate"
# Running the Application
To start the Flask application, run the following command in the terminal:

    python app.py
    The Flask application will run on http://localhost:5000 by default.

# API Endpoints
The following API endpoints are available:

## GET /trigger_report
Description: Triggers the generation of a store status report and saves it to the database.
Response: JSON object with a report_id indicating the ID of the generated report.
## GET /get_report
Description: Fetches a store status report based on the provided report_id.
Parameters: Pass the report_id as a query parameter.
Response: JSON object containing the store status report data.
Database Schema
The application expects the following database schema:

# store_status Table:

store_id: Integer, unique identifier for the store.
timestamp_utc: Timestamp, UTC timestamp indicating the time of the store status update.
status: String, status of the store ("active" or "inactive").
store_hours Table:

store_id: Integer, unique identifier for the store.
day_of_week: Integer, representing the day of the week (0 for Sunday, 1 for Monday, etc.).
start_time_local: Time, the local time at which the store opens.
end_time_local: Time, the local time at which the store closes.
store_timezone Table:

store_id: Integer, unique identifier for the store.
timezone_str: String, representing the store's timezone.
Database Configuration
Modify the db_config dictionary in app.py with the correct MySQL database connection details.

Note
The application uses a local SQLite database to store the generated reports. If you wish to use a different database for report storage, you need to implement the save_report_to_db and fetch_report_from_db functions in app.py accordingly.

This README assumes you have basic knowledge of Flask and database concepts. If you encounter any issues or have questions, feel free to open an issue in this repository.
