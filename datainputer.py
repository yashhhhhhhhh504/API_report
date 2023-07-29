import csv
import mysql.connector
from datetime import datetime

# Connect to the database
try:
    db = mysql.connector.connect(
        host="localhost",
        user="sqluser",
        password="password",
        database="store"
    )
    cursor = db.cursor()

except mysql.connector.Error as e:
    print("Error connecting to MySQL:", e)
    exit()

# Function to print the contents of a table
def print_table_data(table_name):
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        table_data = cursor.fetchall()
        print(f"Contents of {table_name} table:")
        for row in table_data:
            print(row)

    except mysql.connector.Error as e:
        print(f"Error retrieving data from {table_name} table:", e)

# Load store status data
try:
    with open('store_status.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        for row in reader:
            store_id = int(row[0])
            if row[1] == 'active' or row[1] == 'inactive':
                continue
            timestamp_str = row[1].replace(" UTC", "")
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                print(f"Invalid timestamp format in row: {row}")
                continue
            status = row[2]
            cursor.execute(
                "INSERT INTO store_status (store_id, timestamp_utc, status) "
                "VALUES (%s, %s, %s)",
                (store_id, timestamp, status)
            )

    print("Store status data inserted into the database successfully")

except csv.Error as e:
    print("Error reading store_status.csv file:", e)

# Load store hours data
try:
    with open('Menu_hours.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        for row in reader:
            store_id = int(row[0])
            day_of_week = int(row[1])
            start_time = row[2]
            end_time = row[3]
            # Check if the entry already exists in the table
            cursor.execute(
                "SELECT * FROM store_hours WHERE store_id = %s AND day_of_week = %s",
                (store_id, day_of_week)
            )
            existing_entry = cursor.fetchone()

            if existing_entry:
                # Entry already exists, you can either update it or skip the insertion
                print(f"Entry for store_id {store_id} and day_of_week {day_of_week} already exists. Skipping insertion.")
            else:
                # Insert the new entry
                cursor.execute(
                    "INSERT INTO store_hours (store_id, day_of_week, start_time_local, end_time_local) "
                    "VALUES (%s, %s, %s, %s)",
                    (store_id, day_of_week, start_time, end_time)
                )
                print(f"Inserted new entry for store_id {store_id} and day_of_week {day_of_week}")

except csv.Error as e:
    print("Error reading Menu_hours.csv file:", e)

# Load store timezones data
try:
    with open('bq-results-20230125-202210-1674678181880.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        for row in reader:
            store_id = int(row[0])
            timezone_str = row[1]
            cursor.execute(
                "INSERT INTO store_timezone (store_id, timezone_str) "
                "VALUES (%s, %s)",
                (store_id, timezone_str)
            )

    print("Store timezones data inserted into the database successfully")

except csv.Error as e:
    print("Error reading timezone_data.csv file:", e)
db.commit()
# Print the contents of the tables
print_table_data("store_status")
print_table_data("store_hours")
print_table_data("store_timezone")

# Close the database connection
db.close()
