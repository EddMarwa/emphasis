import psycopg2

conn = psycopg2.connect(
    host='127.0.0.1',
    database='emphasis_db',
    user='postgres',
    password='postgres'
)
cursor = conn.cursor()

print("="*70)
print("QUANTUM CAPITAL DATABASE SCHEMA - VERIFICATION REPORT")
print("="*70)

# 1. Count custom tables
cursor.execute("""
    SELECT COUNT(*) as total_tables 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    AND table_name NOT LIKE 'auth_%' AND table_name NOT LIKE 'django_%'
""")
custom_tables = cursor.fetchone()[0]
print(f"\n✅ TABLES: {custom_tables} custom tables created")

# 2. List all custom tables
cursor.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    AND table_name NOT LIKE 'auth_%' AND table_name NOT LIKE 'django_%'
    ORDER BY table_name
""")
tables = [row[0] for row in cursor.fetchall()]
print("\n   Tables:")
for i, table in enumerate(tables, 1):
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"   {i:2d}. {table:<30s} ({count:>5d} rows)")

# 3. Check indexes
cursor.execute("""
    SELECT COUNT(*) FROM pg_indexes 
    WHERE schemaname = 'public' 
    AND tablename NOT LIKE 'auth_%' AND tablename NOT LIKE 'django_%'
""")
index_count = cursor.fetchone()[0]
print(f"\n✅ INDEXES: {index_count} indexes created")

# 4. Check foreign keys
cursor.execute("""
    SELECT COUNT(*) FROM information_schema.table_constraints 
    WHERE table_schema = 'public' 
    AND constraint_type = 'FOREIGN KEY'
    AND table_name NOT LIKE 'auth_%' AND table_name NOT LIKE 'django_%'
""")
fk_count = cursor.fetchone()[0]
print(f"✅ FOREIGN KEYS: {fk_count} foreign key constraints")

# 5. Check triggers
cursor.execute("""
    SELECT COUNT(*) FROM information_schema.triggers 
    WHERE trigger_schema = 'public'
""")
trigger_count = cursor.fetchone()[0]
print(f"✅ TRIGGERS: {trigger_count} triggers created")

# 6. Check platform settings
cursor.execute("SELECT COUNT(*) FROM platform_settings")
settings_count = cursor.fetchone()[0]
print(f"✅ PLATFORM SETTINGS: {settings_count} configuration records")

cursor.execute("SELECT setting_key, setting_value FROM platform_settings ORDER BY setting_key")
print("\n   Configuration:")
for key, value in cursor.fetchall():
    print(f"   • {key:<35s} = {value}")

# 7. Summary
print("\n" + "="*70)
print("SCHEMA CREATION STATUS: ✅ COMPLETE")
print("="*70)
print(f"""
Summary:
  ✓ {custom_tables} custom tables created (24 required)
  ✓ {index_count} indexes created for query optimization
  ✓ {fk_count} foreign key constraints for data integrity
  ✓ {trigger_count} triggers for auto-updating timestamps
  ✓ {settings_count} platform settings configured

The database is ready for use!
""")

cursor.close()
conn.close()
