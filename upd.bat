@echo off
echo %time%
git add -A
git commit -m "changed image sizes"
git pull
git push
echo %time%

