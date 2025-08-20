import os
import shutil

def delete_migration_files(app_name):
    migrations_dir = os.path.join(app_name, 'migrations')
    if os.path.exists(migrations_dir):
        for filename in os.listdir(migrations_dir):
            if filename != '__init__.py' and filename != '__pycache__' and filename.endswith('.py'):
                file_path = os.path.join(migrations_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')

# Clean up migrations for all apps
apps = ['trip', 'interactions', 'accounts']

# Delete the database file
if os.path.exists('db.sqlite3'):
    try:
        os.remove('db.sqlite3')
        print("Deleted: db.sqlite3")
    except Exception as e:
        print(f'Failed to delete db.sqlite3. Reason: {e}')

# Clean up migrations for each app
for app in apps:
    delete_migration_files(app)

print("\nCleanup complete. Now run these commands:")
print("1. python manage.py makemigrations")
print("2. python manage.py migrate")
