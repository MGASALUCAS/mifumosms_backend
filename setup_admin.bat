@echo off
echo ========================================
echo Mifumo SMS Backend - Admin Setup
echo ========================================
echo.

echo Setting up admin user with sample data...
python create_admin_with_data.py

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the server, run:
echo   python manage.py runserver
echo.
echo Then visit: http://localhost:8000/admin/
echo.
pause
