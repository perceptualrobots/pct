@echo off
echo %time%
git add -A
git commit -m "added reset_value for DerivativeWeightedSum"
git pull
git push
echo %time%

