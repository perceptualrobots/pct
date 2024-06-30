@echo off
echo %time%
git add -A
git commit -m "added check limit to fitness error"
git pull
git push
echo %time%

