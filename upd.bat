@echo off
echo %time%
git add -A
git commit -m "before updating ARCDataProcessor, before restructuring ARCEnv"
rem git commit -m "up"
git pull
git push
echo %time%

