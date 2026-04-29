import sys
import os
import allure
import pytest
import json
from pathlib import Path

# 1. 橋接根目錄的模組 (動態路徑)
SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPTS_DIR not in sys.path:
    sys.path.append(SCRIPTS_DIR)

try:
    from data_analyzer import fetch_raw_data, analyze_risk_data
    from config import API_CONFIG
    from report_gen import generate_dashboard_html
except ImportError as e:
    # 預防路徑問題
    raise ImportError(f"載入模組失敗: {e}，請確認目錄路徑是否正確。")

# 2. 在 Session 層級執行一次分析
def get_risk_data():
    wl_data = fetch_raw_data("winlose", API_CONFIG["winlose"])
    mo_data = fetch_raw_data("usermoney", API_CONFIG["usermoney"])
    f_rows, s_rows, det_rows, period, dist = analyze_risk_data(wl_data, mo_data)
    return f_rows, s_rows, det_rows, period, dist

# 獲取分析結果
F_ROWS, S_ROWS, DET_ROWS, PERIOD, DIST = get_risk_data()

@allure.epic("遊戲風險監控報告")
class TestGameRisk:

    @allure.feature("各遊戲風險判定")
    def test_game_risk_status(self, game_info):
        """驗證遊戲勝率是否在正常範圍"""
        game_name = game_info["遊戲名稱"]
        status = game_info["分析結果"]
        win_rate = game_info["殺局贏錢比例"]
        total_rounds = game_info["追殺總局數"]
        wins = game_info["異常局數"]

        # 1. 動態設定標題：讓外層列表直接看到 [結果] 遊戲 | 贏/總 | 勝率
        allure.dynamic.title(f"【{status}】{game_name} | {wins}/{total_rounds} 局 | 勝率: {win_rate}")
        
        # 2. 設定詳細描述
        allure.dynamic.description(f"測試期間: {PERIOD}\n總追殺局數: {total_rounds}\n異常贏錢局數: {wins}\n最終勝率: {win_rate}\n判定結果: {status}")
        
        # 3. 設定嚴重程度 (紅燈等級)
        if status == "異常":
            allure.dynamic.severity(allure.severity_level.BLOCKER)
        elif status == "樣本不足":
            allure.dynamic.severity(allure.severity_level.MINOR)
        else:
            allure.dynamic.severity(allure.severity_level.NORMAL)

        # 4. 附件：該遊戲的詳細明細 (Logs)
        game_details = [r for r in F_ROWS if r.get("遊戲名稱") == game_name]
        allure.attach(
            json.dumps({"summary": game_info, "full_logs": game_details}, ensure_ascii=False, indent=2),
            name=f"{game_name}_數據總覽與Log",
            attachment_type=allure.attachment_type.JSON
        )

        # 5. 斷言判定 (讓報告呈現紅/綠/黃燈)
        if status == "異常":
            pytest.fail(f"【判定異常】遊戲 {game_name} 勝率高達 {win_rate}，超出警戒門檻！")
        elif status == "樣本不足":
            pytest.skip(f"【樣本不足】遊戲 {game_name} 僅有 {total_rounds} 局數據，無法進行準確風險評估。")
        else:
            assert status == "正常", f"預期狀態為正常，但實際為 {status}"

def pytest_generate_tests(metafunc):
    """動態生成測試案例，每個遊戲一個"""
    if "game_info" in metafunc.fixturenames:
        metafunc.parametrize("game_info", S_ROWS, ids=[r["遊戲名稱"] for r in S_ROWS])

