"""
雲端同步模組 - 負責與 Google Sheets 進行數據同步與格式化
"""
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import SERVICE_ACCOUNT_FILE, GOOGLE_SHEET_NAME

class SheetSyncManager:
    def __init__(self, sheet_name=GOOGLE_SHEET_NAME):
        self.sheet_name = sheet_name
        self.ss = None
        self.worksheets = {}

    def authenticate(self):
        """執行 Google API 認證"""
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            print(f"[ERROR] 找不到授權檔案: {SERVICE_ACCOUNT_FILE}")
            return False
        
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
            client = gspread.authorize(creds)
            self.ss = client.open(self.sheet_name)
            self.worksheets = {s.title: s for s in self.ss.worksheets()}
            return True
        except Exception as e:
            print(f"[ERROR] 認證或開啟試算表失敗: {e}")
            return False

    def reset_worksheet(self, title, rows, cols, tab_color):
        """重置或建立工作表"""
        if title in self.worksheets:
            sheet = self.worksheets[title]
            sheet.clear()
        else:
            sheet = self.ss.add_worksheet(title=title, rows=str(rows), cols=str(cols))
        
        # 設定分頁顏色與基礎樣式
        try:
            self.ss.batch_update({
                "requests": [{
                    "updateSheetProperties": {
                        "properties": {"sheetId": sheet.id, "tabColor": tab_color},
                        "fields": "tabColor"
                    }
                }]
            })
            sheet.format(f"A1:Z{max(rows, 100)}", {
                "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                "textFormat": {"bold": False, "foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0}, "fontSize": 10}
            })
        except: pass
        return sheet

    def sync_data(self, summary_data, detail_data, processed_data, html_content):
        """同步所有數據到雲端"""
        if not self.authenticate(): return None

        print("[SYNC] 正在同步數據至 Google Sheets...")
        
        # 1. 更新分析報告
        s_sheet = self.reset_worksheet("異常分析報告", 100, 6, {"red": 0.8, "green": 0.1, "blue": 0.1})
        s_headers = ["遊戲名稱", "追殺總局數", "異常局數", "殺局贏錢比例", "分析結果"]
        s_rows = [s_headers] + [
            [r.get(h, "") if h != "分析結果" else (("❗ " + r[h]) if r[h] == "異常" else r[h]) for h in s_headers] 
            for r in summary_data
        ]
        s_sheet.update(range_name='A1', values=s_rows)
        
        # 條件格式化
        fmts = []
        for i, r in enumerate(summary_data):
            if r["分析結果"] == "異常":
                fmts.append({"range": f"A{i+2}:E{i+2}", "format": {"backgroundColor": {"red": 0.98, "green": 0.9, "blue": 0.9}, "textFormat": {"bold": True, "foregroundColor": {"red": 0.7}}}})
            elif r["分析結果"] == "樣本不足":
                fmts.append({"range": f"A{i+2}:E{i+2}", "format": {"backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95}, "textFormat": {"foregroundColor": {"red": 0.4}}}})
        if fmts: s_sheet.batch_format(fmts)

        # 2. 更新異常明細
        if detail_data:
            det_sheet = self.reset_worksheet("異常明細資料", 2000, 15, {"red": 0.8, "green": 0.1, "blue": 0.1})
            det_headers = ["遊戲名稱", "殺局贏錢比例", "會員帳號", "房間類型", "投注金額", "損益", "遊戲序號"]
            det_rows = [det_headers] + [[r.get(h, "N/A") for h in det_headers] for r in sorted(detail_data, key=lambda x: (x.get("遊戲名稱", ""), x.get("殺局贏錢比例", "")))]
            det_sheet.update(range_name='A1', values=det_rows)
            det_sheet.freeze(rows=1)
            det_sheet.format("A1:G1", {"backgroundColor": {"red": 0.5, "green": 0.0, "blue": 0.0}, "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}})

        # 3. 更新詳細原始資料 (分頁隱藏在後面)
        if processed_data:
            d_sheet = self.reset_worksheet("詳細資料", 5000, 25, {"red": 0.1, "green": 0.4, "blue": 0.8})
            d_headers = list(processed_data[0].keys())
            d_rows = [d_headers] + [[r.get(h, "") for h in d_headers] for r in processed_data]
            d_sheet.update(range_name='A1', values=d_rows)
            d_sheet.format(f"A1:{chr(64+min(len(d_headers),26))}1", {"backgroundColor": {"red": 0.0, "green": 0.2, "blue": 0.5}, "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}})

        # 4. 同步 WebApp 原始碼並隱藏
        web_sheet = self.reset_worksheet("WebApp_Source", 1, 1, {"red": 0.5, "green": 0.5, "blue": 0.5})
        web_sheet.update(range_name='A1', values=[[html_content]])
        self.ss.batch_update({"requests": [{"updateSheetProperties": {"properties": {"sheetId": web_sheet.id, "hidden": True}, "fields": "hidden"}}]})

        print(f"[SUCCESS] 數據已同步至雲端試算表。")
        return self.ss.url
