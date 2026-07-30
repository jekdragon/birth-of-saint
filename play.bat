@echo off
echo ==========================================
echo   Рождение святого - запуск в браузере
echo ==========================================
echo.
echo Сервер запускается на http://localhost:8081/
echo.
echo После загрузки нажми на зеленую кнопку "Click to start"
echo.
echo Для остановки нажми Ctrl+C
echo.
cd /d "%~dp0"
python -m pygbag --port 8081 .
pause
