import os
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# ── 靜態檔案（前端 HTML）──────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")


# ── 資料模型 ──────────────────────────────────────────────────────────────────
class QuestionnaireData(BaseModel):
    # 基本資料
    patient_id: str
    name: str
    birth: str
    followup: str

    # 經血 PBAC
    no_blood: bool = False
    pl: int = 0; pm: int = 0; ph: int = 0
    tl: int = 0; tm: int = 0; th: int = 0
    cs: int = 0; cl: int = 0; ac: int = 0
    blood_score: int = 0

    # 經痛 VAS
    no_pain: bool = False
    pain_val: int = 0

    # 頻尿 UDI-6
    no_udi: bool = False
    udi_0: int = 0; udi_1: int = 0; udi_2: int = 0
    udi_3: int = 0; udi_4: int = 0; udi_5: int = 0
    udi_total: int = 0


# ── 發信函數 ──────────────────────────────────────────────────────────────────
def send_gmail(data: QuestionnaireData):
    smtp_user     = os.environ.get("EMAIL_USER", "cgmh.hifu.staff@gmail.com")
    smtp_password = os.environ["EMAIL_PASSWORD"]
    smtp_receiver = os.environ.get("EMAIL_RECEIVER", "cgmh.hifu.center@gmail.com")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ① 建立 Excel 附件
    df = pd.DataFrame([{
        "病歷號碼":       data.patient_id,
        "姓名":           data.name,
        "出生年月日":     data.birth,
        "追蹤期間":       data.followup,
        "填寫時間":       now_str,
        "經血分數(PBAC)": data.blood_score,
        "經痛分數(VAS)":  data.pain_val,
        "頻尿分數(UDI)":  data.udi_total,
        "衛生棉(輕/中/重)": f"{data.pl}/{data.pm}/{data.ph}",
        "棉條(輕/中/重)":   f"{data.tl}/{data.tm}/{data.th}",
        "血塊(小/大)/滲漏": f"{data.cs}/{data.cl}/{data.ac}",
        "UDI明細(Q1~Q6)":  f"{data.udi_0},{data.udi_1},{data.udi_2},{data.udi_3},{data.udi_4},{data.udi_5}",
    }])

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)

    # ② 組 Email
    msg = MIMEMultipart()
    msg["From"]    = smtp_user
    msg["To"]      = smtp_receiver
    msg["Subject"] = f"【海扶問卷】{data.name} — {data.followup}"

    html_body = f"""
    <div style="font-family:sans-serif; max-width:500px;">
      <h2 style="color:#00695C; border-bottom:2px solid #B2DFDB; padding-bottom:8px;">
        🏥 海扶治療中心 — 問卷回覆通知
      </h2>
      <table style="width:100%; border-collapse:collapse; font-size:15px;">
        <tr><td style="padding:8px; color:#546E7A;">姓名</td>
            <td style="padding:8px; font-weight:700;">{data.name}</td></tr>
        <tr style="background:#F5F5F5;">
            <td style="padding:8px; color:#546E7A;">病歷號</td>
            <td style="padding:8px; font-weight:700;">{data.patient_id}</td></tr>
        <tr><td style="padding:8px; color:#546E7A;">追蹤期間</td>
            <td style="padding:8px; font-weight:700;">{data.followup}</td></tr>
        <tr style="background:#F5F5F5;">
            <td style="padding:8px; color:#546E7A;">🩸 經血 PBAC</td>
            <td style="padding:8px; font-weight:700; color:#D84315;">{data.blood_score} 分</td></tr>
        <tr><td style="padding:8px; color:#546E7A;">⚡ 經痛 VAS</td>
            <td style="padding:8px; font-weight:700; color:#D84315;">{data.pain_val} 分</td></tr>
        <tr style="background:#F5F5F5;">
            <td style="padding:8px; color:#546E7A;">🚽 頻尿 UDI-6</td>
            <td style="padding:8px; font-weight:700; color:#D84315;">{data.udi_total} 分</td></tr>
      </table>
      <p style="color:#90A4AE; font-size:13px; margin-top:16px;">
        填寫時間：{now_str}<br>詳細數據請查閱附件 Excel。
      </p>
    </div>
    """
    msg.attach(MIMEText(html_body, "html"))

    filename = f"{data.name}_{data.followup}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    part = MIMEApplication(buf.read(), Name=filename)
    part["Content-Disposition"] = f'attachment; filename="{filename}"'
    msg.attach(part)

    # ③ 發送
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_user, smtp_password)
        server.send_message(msg)


# ── API 端點 ──────────────────────────────────────────────────────────────────
@app.post("/api/submit")
def submit(data: QuestionnaireData):
    try:
        send_gmail(data)
        return {"ok": True, "message": "問卷已送出，報告已發送至醫護信箱。"}
    except KeyError as e:
        raise HTTPException(500, f"環境變數未設定：{e}")
    except Exception as e:
        raise HTTPException(500, f"發送失敗：{str(e)}")


# ── 本地開發用 ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
