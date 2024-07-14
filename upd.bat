@echo off
echo %time%
git add -A
rem git commit -m "after restructuring ARCEnv"
git commit -m "up"
git pull
git push
echo %time%

