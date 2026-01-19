import psycopg2

conn = psycopg2.connect(host='127.0.0.1', database='emphasis_db', user='postgres', password='postgres')
cursor = conn.cursor()

# List all tables
cursor.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name
""")
tables = cursor.fetchall()
print('=== TABLES CREATED ===')
for i, (table,) in enumerate(tables, 1):
    print(f'{i}. {table}')
print(f'\nTotal: {len(tables)} tables')

# Check platform_settings
print('\n=== PLATFORM SETTINGS ===')
cursor.execute("SELECT COUNT(*) FROM platform_settings")
count = cursor.fetchone()[0]
print(f'Platform settings records: {count}')

cursor.close()
conn.close()
