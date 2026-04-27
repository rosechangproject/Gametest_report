"""
中央設定模組 - 收集所有專案變數與判定閾值
"""

# ========================== 核心連線設定 ==========================
# Google Sheets WebApp 網址 (用於儀表板快速入口)
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxS6SNNDApHfaR98DGmo-VpHE1f29CWxLoFcnK3OcwDzqkx9f1Lxgr1WKAMSJ9_LKNu/exec"

# 資料介面設定
API_CONFIG = {
    "winlose": "http://192.168.37.6:8087/practice_data?key=winlose",
    "usermoney": "http://192.168.37.6:8087/practice_data?key=usermoney"
}

# ========================== 業務分析邏輯設定 ==========================
# 門檻值定義
RISK_THRESHOLD_WR = 0.05      # 勝率異常判定門檻 (5%)
MIN_SAMPLE_SIZE = 50          # 樣本數判定門檻 (50局)

# 風險優先級定義 (用於排序)
# 異常(0) > 正常(1) > 樣本不足(2)
STATUS_WEIGHTS = {
    "異常": 0,
    "正常": 1,
    "樣本不足": 2
}

# 最終定義：殺局房型
CHASING_TYPES = ['B', 'T', 'K', 'ptk', 'PTK']

# ========================== 雲端同步設定 ==========================
GOOGLE_SHEET_NAME = "QA測試分析報告"
SERVICE_ACCOUNT_FILE = "service_account.json"

# 試算表欄位翻譯對照
COLUMN_MAP = {
    "account": "會員帳號", 
    "gameName": "遊戲名稱", 
    "roomType": "房間類型", 
    "profit": "損益",
    "gameNo": "遊戲序號", 
    "gameUserNO": "玩家序號", 
    "gameEndTime": "建立時間", 
    "money": "剩餘點數",
    "allBet": "投注金額", 
    "cellScore": "有效投注"
}
