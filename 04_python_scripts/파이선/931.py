import mysql.connector
import pandas as pd
import numpy as np

# Ensure you have openpyxl installed
# pip install openpyxl

df = pd.read_excel('111cement50.xlsx')

db_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='!eomtaejun01',
    database='regression_db'
)

# Create a cursor
cursor = db_connection.cursor()

# Drop the existing table if it exists
drop_table_query = "DROP TABLE IF EXISTS data_table"
cursor.execute(drop_table_query)

# Create the table again
create_table_query = """
CREATE TABLE data_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    column1 FLOAT,
    column2 FLOAT,
    column3 FLOAT
);
"""
cursor.execute(create_table_query)

# Function to map pandas dtypes to MySQL types
def get_mysql_type(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return "INT"
    elif pd.api.types.is_float_dtype(dtype):
        return "FLOAT"
    elif pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    else:
        return "VARCHAR(255)"

# Define column definitions for table creation based on DataFrame dtypes
columns = df.columns
column_definitions = ",\n    ".join([f"`{col}` {get_mysql_type(dtype)}" for col, dtype in zip(columns, df.dtypes)])

# Insert data into the table
insert_query = f"""
    INSERT INTO data_table ({", ".join([f"`{col}`" for col in columns])})
    VALUES ({", ".join(["%s" for _ in columns])})
"""

# Insert data into the table
for _, row in df.iterrows():
    cursor.execute(insert_query, tuple(row))

# Commit the changes
db_connection.commit()

# Close the cursor and connection
cursor.close()
db_connection.close()
