import glob
import os


def delete_migrations_in_app(app_path):
    migrations_path = os.path.join(app_path, "migrations")
    if os.path.exists(migrations_path):
        migration_files = glob.glob(os.path.join(migrations_path, "*.py"))
        migration_files = [f for f in migration_files if not f.endswith("__init__.py")]

        for file in migration_files:
            try:
                os.remove(file)
                print(f"Deleted: {file}")
            except Exception as e:
                print(f"Failed to delete {file}: {e}")


def delete_all_migrations(core_path):
    if not os.path.exists(core_path):
        print(f"The specified path '{core_path}' does not exist.")
        return

    for root, dirs, files in os.walk(core_path):
        for dir in dirs:
            app_path = os.path.join(root, dir)
            if os.path.exists(os.path.join(app_path, "migrations")):
                delete_migrations_in_app(app_path)


if __name__ == "__main__":
    core_folder_path = "kns"
    delete_all_migrations(core_folder_path)
