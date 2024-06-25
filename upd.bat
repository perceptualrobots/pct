@echo off
echo %time%
git add -A
git commit -m "added images to display"
git pull
git push
echo %time%

