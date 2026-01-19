import psycopg2
from psycopg2 import sql

# Read the SQL schema file
with open('d:\\PROJECTS\\emphasis\\quantum_capital_schema.sql', 'r') as f:
    schema_sql = f.read()

# Split into individual statements
statements = schema_sql.split(';')
statements = [s.strip() for s in statements if s.strip()]

# Connect to database
try:
    conn = psycopg2.connect(
        host='127.0.0.1',
        database='emphasis_db',
        user='postgres',
        password='postgres',
        port='5432'
    )
    cursor = conn.cursor()
    
    # Execute each statement
    for i, statement in enumerate(statements, 1):
        try:
            cursor.execute(statement)
            print(f"✓ Statement {i} executed successfully")
        except Exception as e:
            print(f"✗ Error in statement {i}: {str(e)}")
            conn.rollback()
            continue
    
    conn.commit()
    cursor.close()
    conn.close()
    print("\n✅ Schema creation completed successfully!")
    
    # Verify the tables
    conn = psycopg2.connect(
        host='127.0.0.1',
        database='emphasis_db',
        user='postgres',
        password='postgres',
        port='5432'
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) as total_tables 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    result = cursor.fetchone()
    print(f"\n📊 Total tables created: {result[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Connection failed: {str(e)}")
