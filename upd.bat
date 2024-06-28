@echo off
echo %time%
git add -A
git commit -m "before adding dims to state"
git pull
git push
echo %time%

