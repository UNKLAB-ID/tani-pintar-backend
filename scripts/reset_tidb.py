from django.conf import settings
from django.db import connection


def run():
    db_name = settings.DATABASES["default"]["NAME"]

    with connection.cursor() as cursor:
        print(f"Dropping database {db_name}...")  # noqa: T201
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
        cursor.execute(f"CREATE DATABASE {db_name};")
        print(f"Database {db_name} reset successfully!")  # noqa: T201
