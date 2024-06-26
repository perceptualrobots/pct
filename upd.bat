@echo off
echo %time%
git add -A
git commit -m "after manual change of arc screen size"
git pull
git push
echo %time%

