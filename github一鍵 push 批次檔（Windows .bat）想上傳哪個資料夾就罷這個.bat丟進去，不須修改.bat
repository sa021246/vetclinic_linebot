@echo off宣告目標資料夾
cd /d %~dp0
echo --------------------------
echo Git status
git status

echo --------------------------
echo Git add .
git add .

echo --------------------------
git commit -m "update requirements.txt"


echo --------------------------
git push origin main

echo --------------------------
echo ✅ Push 完成！
pause
