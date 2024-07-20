@echo off
echo %time%
git add -A
rem git commit -m "after modifying ARCDataProcessor 001 ARCEnv 002"
git commit -m "up"
git pull
git push
echo %time%

