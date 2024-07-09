@echo off
echo %time%
git add -A
-- git commit -m "before restructuring ARCEnv"
git commit -m "up"
git pull
git push
echo %time%

