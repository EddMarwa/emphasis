import psycopg2

conn = psycopg2.connect(
    host='127.0.0.1',
    database='emphasis_db',
    user='postgres',
    password='postgres'
)
conn.autocommit = True
cursor = conn.cursor()

# Drop existing users table and related constraints
print("Dropping existing tables...")
try:
    cursor.execute("DROP TABLE IF EXISTS users CASCADE")
    print("✓ Dropped users table")
except Exception as e:
    print(f"Note: {e}")

conn.autocommit = False

# Read and execute the schema file
with open('d:\\PROJECTS\\emphasis\\quantum_capital_schema.sql', 'r') as f:
    content = f.read()

# Use psycopg2's built-in function to execute multiple statements
from psycopg2 import sql as psql
try:
    cursor.execute(content)
    conn.commit()
    print("\n✅ All schema statements executed successfully!")
except Exception as e:
    print(f"\n❌ Error: {e}")
    conn.rollback()

# Verify
cursor.execute("""
    SELECT COUNT(*) as total_tables 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
""")
total_tables = cursor.fetchone()[0]

cursor.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    ORDER BY table_name
""")
tables = [row[0] for row in cursor.fetchall()]

print(f"\n📊 Total tables: {total_tables}")
print(f"🗂️  Custom tables created:")
custom_tables = [t for t in tables if not t.startswith('auth_') and not t.startswith('django_')]
for t in custom_tables:
    print(f"   - {t}")

cursor.close()
conn.close()
