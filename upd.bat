@echo off
echo %time%
git add -A
git commit -m update
git pull
git push
echo %time%

