import os
import shutil
import subprocess
from pathlib import Path

# 引入 config.py 的動態路徑設定
from config import SCRIPTS_DIR, BASE_DIR

def run_api_tests():
    """執行風險監控測試並全自動生成報告"""
    results_dir = Path(BASE_DIR) / "allure-results"
    report_dir = Path(BASE_DIR) / "allure-report"
    
    # 1. 強制清理舊數據 (確保報告不會顯示 0 或舊測項)
    print("正在清理舊的測試數據...")
    if results_dir.exists():
        shutil.rmtree(results_dir)
    if report_dir.exists():
        shutil.rmtree(report_dir)
    
    results_dir.mkdir(exist_ok=True)
    report_dir.mkdir(exist_ok=True)

    print("開始執行遊戲風險監控分析...")
    # 只執行風險分析測試，並將結果存入 results_dir
    test_file_path = Path(SCRIPTS_DIR) / "test_case" / "test_risk_report.py"
    cmd_pytest = [
        "pytest",
        str(test_file_path),
        "--alluredir", str(results_dir)
    ]
    test_result = subprocess.run(cmd_pytest).returncode

    if test_result in {0, 1}:
        print("\n[SUCCESS] 數據分析完成。")

        # 檢查環境中是否有 allure 指令
        allure_check = subprocess.run("allure --version", shell=True, capture_output=True)
        
        if allure_check.returncode == 0:
            print("正在生成 Allure HTML 報告...")
            cmd_allure = f"allure generate {results_dir} -o {report_dir} --clean --single-file"
            subprocess.run(cmd_allure, shell=True)
            
            report_file = report_dir / "index.html"
            print("\n" + "═"*50)
            print(f"報告已更新！請在終端機執行以查看最新結果：")
            print(f"   allure serve {results_dir}")
            print("═"*50)
        else:
            print("\n系統未安裝 Allure 指令，請安裝後執行: allure serve ./allure-results")
    else:
        print(f"\n測試執行異常，錯誤碼: {test_result}")

if __name__ == "__main__":
    run_api_tests()