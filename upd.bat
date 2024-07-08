@echo off
echo %time%
git add -A
-- git commit -m "before moving file load to ARC"
git commit -m "up"
git pull
git push
echo %time%

