@echo off
echo %time%
git add -A
git commit -m "added dynamic positions of elements"
git pull
git push
echo %time%

