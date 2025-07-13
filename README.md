# Railway 部署教學

1️⃣ 在 Railway.app 註冊帳號。

2️⃣ 建立新專案，選擇 GitHub 並連接這個專案。

3️⃣ 將 `CHANNEL_ACCESS_TOKEN` 和 `CHANNEL_SECRET` 設為 Railway 專案的環境變數。

4️⃣ Railway 會自動執行：
```
 python vetclinic_demo_app.py
```

5️⃣ 部署完成後，會有固定公開網址。
例如：https://你的專案名稱.up.railway.app

6️⃣ 把 LINE Webhook URL 改為：
```
https://你的專案名稱.up.railway.app/callback
```

7️⃣ 程式內的圖片網址會自動用 Railway 網址發送，無需手動修改。
