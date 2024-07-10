@echo off
echo %time%
git add -A
git commit -m "before modifying ARCDataProcessor"
rem git commit -m "up"
git pull
git push
echo %time%

