@echo off
echo Starting Mifumo SMS Servers
echo ==========================

echo Starting Django server...
start "Django Server" cmd /k "python manage.py runserver"

echo Waiting for Django to start...
timeout /t 5 /nobreak > nul

echo Starting Purchase Page server...
start "Purchase Page Server" cmd /k "python serve_purchase_page.py"

echo Waiting for Purchase Page to start...
timeout /t 3 /nobreak > nul

echo.
echo ==========================
echo SERVERS STARTED!
echo ==========================
echo Django API: http://localhost:8000
echo Purchase Page: http://localhost:8080/purchase_packages.html
echo.
echo Opening purchase page...
start http://localhost:8080/purchase_packages.html

echo.
echo Both servers are running in separate windows.
echo Close the command windows to stop the servers.
pause
