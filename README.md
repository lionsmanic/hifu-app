# 海扶治療中心 — 患者追蹤問卷

純 HTML 前端 + FastAPI 後端 + Gmail SMTP，無 Streamlit 框架。

## Email 設定（已配置）
- 寄信：cgmh.hifu.staff@gmail.com
- 收信：cgmh.hifu.center@gmail.com

## 專案結構

```
hifu-app/
├── main.py              ← FastAPI 後端（API + 靜態服務）
├── requirements.txt
├── render.yaml          ← Render 一鍵部署設定
└── static/
    └── index.html       ← 前端（全部 CSS/JS 內嵌）
```

---

## 第一步：取得 Gmail App Password（必做！）

> cgmh.hifu.staff@gmail.com 這個帳號要操作

1. 登入 cgmh.hifu.staff@gmail.com
2. 前往 https://myaccount.google.com/security
3. 確認「兩步驟驗證」已開啟（若未開啟先開啟）
4. 在安全性頁面搜尋「應用程式密碼」
5. 新增 → 名稱填「hifu-app」→ 產生
6. 複製 16 碼密碼（格式：xxxx xxxx xxxx xxxx）
7. **把這個密碼貼到下方 Render 環境變數的 EMAIL_PASSWORD**

> ⚠️ 這個 App Password 和 Gmail 登入密碼不同，請妥善保管

---

## 第二步：部署到 Render

### 2-1 推上 GitHub
```bash
git init
git add .
git commit -m "init"
# 在 github.com 新建一個 repo（例如 hifu-app），然後：
git remote add origin https://github.com/你的帳號/hifu-app.git
git push -u origin main
```

### 2-2 Render 設定
1. 前往 https://render.com → 登入 → **New → Web Service**
2. 連結你的 GitHub repo
3. Render 會自動讀取 `render.yaml`，Build/Start Command 不用動
4. 進入 **Environment** 頁籤，**只需要新增一個**環境變數：

| Key              | Value                              |
|------------------|------------------------------------|
| `EMAIL_PASSWORD` | 第一步取得的 16 碼 App Password     |

（EMAIL_USER 和 EMAIL_RECEIVER 已經寫在 render.yaml 裡了）

5. 點擊 **Deploy** → 約 2 分鐘後取得公開網址 ✅

---

## 本地測試（選用）

```bash
pip install -r requirements.txt

# Mac/Linux：
export EMAIL_PASSWORD="xxxx xxxx xxxx xxxx"

# Windows CMD：
set EMAIL_PASSWORD=xxxx xxxx xxxx xxxx

python main.py
# 開啟瀏覽器 → http://localhost:8000
```

---

## 注意事項

- Render **免費方案**閒置 15 分鐘後會休眠，首次開啟需等約 30 秒喚醒
- 若需要永不休眠，可升級 Render Starter（$7/月）或改用 Railway
- 日後要換收信 Email，直接修改 render.yaml 的 EMAIL_RECEIVER 再 push 即可
