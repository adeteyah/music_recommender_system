import pandas as pd
import sqlite3

# Define your variables here
csv_file = r'C:\Users\Adeteyah\Documents\music_recommender_system\scripts\archive\dataset_1.csv'
db_file = r'data\main.db'
table_name = 'dataset_1'


def csv_to_sqlite(csv_file, db_file, table_name):
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file)

        # Connect to SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect(db_file)

        # Write the DataFrame to the SQLite table
        df.to_sql(table_name, conn, if_exists='replace', index=False)

        # Close the database connection
        conn.close()
        print(f"CSV data has been successfully imported into {
              table_name} table in {db_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Call the function with the specified variables
csv_to_sqlite(csv_file, db_file, table_name)
