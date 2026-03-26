@echo off
REM Script para automatizar add + commit + push

set /p mensaje=Escribe el mensaje del commit: 
git add .
git commit -m "%mensaje%"
git push origin main
