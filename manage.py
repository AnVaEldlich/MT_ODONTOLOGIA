#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

try:
    import MySQLdb  # noqa: F401
except ImportError:
    import pymysql

    pymysql.install_as_MySQLdb()


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Web_odontologia.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "There was an error importing Django. "
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
