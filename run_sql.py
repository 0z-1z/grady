import psycopg2

# Database connection parameters (using your connection details)
db_params = {
    'dbname': 'postgres',  # Your database name
    'user': 'postgres.gnjphsjmpwitwskopgxf',  # Your username
    'password': '-4Yd@msU7G65k5S',  # Your password
    'host': 'aws-0-eu-central-1.pooler.supabase.com',  # Supabase host
    'port': '6543',  # Supabase port
    'sslmode': 'require',  # SSL mode
}

# Connect to the PostgreSQL server
conn = psycopg2.connect(**db_params)
cur = conn.cursor()

# Read the SQL script from the file
with open('setup_2.sql', 'r') as file:
    sql_script = file.read()

# Execute the SQL script
cur.execute(sql_script)

# Commit changes (if the script modifies the database)
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

print("SQL script executed successfully.")
