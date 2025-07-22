@echo off
cd /d %~dp0
echo --------------------------
echo Git add .
git add .

echo --------------------------
echo Git commit
git commit -m "fix: lock aiohttp version"

echo --------------------------
echo Git push
git push origin main

echo --------------------------
echo ✅ Push 完成！
pause
