import psycopg2
import re

# Connect to database
conn = psycopg2.connect(
    host='127.0.0.1',
    database='emphasis_db',
    user='postgres',
    password='postgres'
)
cursor = conn.cursor()

# Read the schema file
with open('d:\\PROJECTS\\emphasis\\quantum_capital_schema.sql', 'r') as f:
    content = f.read()

# Split by looking for the specific table and index patterns
# Find all CREATE statements between comments
statements = []
lines = content.split('\n')
current_statement = []

for line in lines:
    # Skip empty lines and comments
    if line.strip() == '' or line.strip().startswith('--'):
        if current_statement:
            statements.append('\n'.join(current_statement))
            current_statement = []
    else:
        current_statement.append(line)
        # Check if this line ends a statement (ends with ;)
        if line.rstrip().endswith(';'):
            statements.append('\n'.join(current_statement))
            current_statement = []

# Remove empty statements
statements = [s.strip() for s in statements if s.strip()]

print(f"Total statements to execute: {len(statements)}\n")

# Execute each statement
executed = 0
failed = 0

for i, statement in enumerate(statements, 1):
    if not statement or statement.strip() == '':
        continue
    try:
        cursor.execute(statement)
        executed += 1
        # Print only major table creations
        if 'CREATE TABLE' in statement:
            table_match = re.search(r'CREATE TABLE (\w+)', statement)
            if table_match:
                print(f"✓ Table '{table_match.group(1)}' created")
        elif 'INSERT INTO' in statement:
            print(f"✓ INSERT statement executed")
        elif 'CREATE TRIGGER' in statement:
            trigger_match = re.search(r'CREATE TRIGGER (\w+)', statement)
            if trigger_match:
                print(f"✓ Trigger '{trigger_match.group(1)}' created")
        elif 'CREATE INDEX' in statement:
            idx_match = re.search(r'CREATE INDEX (\w+)', statement)
            if idx_match:
                print(f"✓ Index '{idx_match.group(1)}' created")
        elif 'CREATE OR REPLACE FUNCTION' in statement:
            func_match = re.search(r'CREATE OR REPLACE FUNCTION (\w+)', statement)
            if func_match:
                print(f"✓ Function '{func_match.group(1)}' created")
    except Exception as e:
        failed += 1
        if 'already exists' not in str(e):
            print(f"✗ Error in statement: {str(e)[:100]}")

conn.commit()

# Verify tables
print("\n" + "="*50)
print("VERIFICATION")
print("="*50)

cursor.execute("""
    SELECT COUNT(*) as total_tables 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
""")
total_tables = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*) FROM platform_settings
""")
try:
    settings_count = cursor.fetchone()[0]
except:
    settings_count = 0

cursor.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    ORDER BY table_name
""")
tables = cursor.fetchall()

print(f"\n✅ Schema creation completed!")
print(f"📊 Total statements executed: {executed}")
print(f"⚠️  Failed statements: {failed}")
print(f"📋 Total tables created: {total_tables}")
print(f"⚙️  Platform settings records: {settings_count}")

print(f"\n📝 Tables in database:")
for i, (table,) in enumerate(tables, 1):
    # Filter out Django tables
    if not table.startswith('auth_') and not table.startswith('django_'):
        print(f"  {i}. {table}")

cursor.close()
conn.close()
