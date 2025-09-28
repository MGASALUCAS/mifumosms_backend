@echo off
REM Simple alias for createsuperuser that works with custom user model
python manage.py create_admin --email %1 --first-name %2 --last-name %3 --password %4
