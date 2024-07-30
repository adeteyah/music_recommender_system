import sqlite3

# Define your database file
db_file = 'data/main.db'


def duplicate_table(db_file, old_table_name, new_table_name):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Get the schema of the old table
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{
                       old_table_name}'")
        create_table_sql = cursor.fetchone()[0]

        # Modify the schema to create the new table
        create_table_sql = create_table_sql.replace(
            old_table_name, new_table_name)

        # Create the new table with the same schema
        cursor.execute(create_table_sql)

        # Copy data from the old table to the new table
        cursor.execute(
            f"INSERT INTO {new_table_name} SELECT * FROM {old_table_name}")

        # Commit the transaction
        conn.commit()
        print(f"Table {old_table_name} has been successfully duplicated to {
              new_table_name}.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the database connection
        conn.close()


# Call the function with the specified variables
duplicate_table(db_file, 'songs_backup', 'songs')
