@echo off
echo %time%
git add -A
git commit -m "after adding my code for ensuring env is not less than 1x1"
git pull
git push
echo %time%

