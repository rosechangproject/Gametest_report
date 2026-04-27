"""
QA 風險監控儀表板 - 啟動主程式
功能：協調整合資料分析、報表生成與雲端同步
版本：v2.5 (Modular Refactored)
"""
import sys
from config import API_CONFIG, WEBAPP_URL
from data_analyzer import fetch_raw_data, analyze_risk_data
from report_gen import generate_dashboard_html
from cloud_sync import SheetSyncManager

def run_workflow():
    print("\n" + "═"*60)
    print(" 🚀 QA 風險監控自動化分析系統 v2.5 啟動中...")
    print("═"*60 + "\n")

    # 1. 獲取原始資料 (WinLose 與 UserMoney)
    wl_data = fetch_raw_data("winlose", API_CONFIG["winlose"])
    mo_data = fetch_raw_data("usermoney", API_CONFIG["usermoney"])

    if not wl_data:
        print("[CRITICAL] 無法獲取基礎 WinLose 資料，分析中斷。")
        return

    # 2. 核心分析邏輯
    # f_rows: 明細翻譯, s_rows: 摘要報告, det_rows: 異常明細, period: 測試期間, dist: 風險分佈
    f_rows, s_rows, det_rows, period, dist = analyze_risk_data(wl_data, mo_data)

    # 3. 生成本地可視化 HTML 儀表板
    html_path = generate_dashboard_html(s_rows, period, dist)
    print(f"[SUCCESS] 本地儀表板已產出: {html_path}")

    # 4. 讀取 HTML 內容準備同步至雲端
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"[ERROR] 讀取 HTML 內容失敗: {e}")
        return

    # 5. 執行雲端同步 (Google Sheets)
    sync_manager = SheetSyncManager()
    sheet_url = sync_manager.sync_data(s_rows, det_rows, f_rows, html_content)

    # 6. 完工報告
    if sheet_url:
        print("\n" + "╔" + "═"*78 + "╗")
        print(f"║  🏁 任務完成！數據已成功同步並生成視覺化儀表板                     ║")
        print(f"╠" + "═"*78 + "╣")
        print(f"║  📊 儀表板 WebApp：{WEBAPP_URL:56} ║")
        print(f"║  📂 Google 試算表：{sheet_url:56} ║")
        print(f"╚" + "═"*78 + "╝\n")
    else:
        print("\n[FINISH] 分析完成，本地報表已產出，但雲端同步未執行或失敗。")

if __name__ == "__main__":
    # 強制 stdout 使用 UTF-8 避免 Windows 環境亂碼
    if sys.stdout.encoding != 'utf-8':
        try:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        except: pass
        
    try:
        run_workflow()
    except KeyboardInterrupt:
        print("\n[INFO] 使用者手動取消程序。")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] 系統發生非預期錯誤: {e}")
