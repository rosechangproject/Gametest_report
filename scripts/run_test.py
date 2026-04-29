import os
import shutil
import subprocess
from pathlib import Path

# 引入 config.py 的動態路徑設定
from config import SCRIPTS_DIR, BASE_DIR, REPORT_DIR_PATH

def run_api_tests():
    """執行風險監控測試並全自動生成報告"""
    results_dir = Path(BASE_DIR) / "allure-results"
    # 這是 Allure 產出整包檔案的暫存資料夾
    temp_report_dir = Path(BASE_DIR) / "allure_temp" 
    # 這是妳 index.html 連結真正要看的那個檔案
    final_report_file = Path(REPORT_DIR_PATH) / "allure-report.html"
    
    # 1. 強制清理舊數據 (確保報告不會顯示 0 或舊測項)
    print("正在清理舊的測試數據...")
    
    if temp_report_dir.exists(): # 👈 改成 temp_report_dir
     shutil.rmtree(temp_report_dir) # 👈 改成 temp_report_dir

    temp_report_dir.mkdir(exist_ok=True) # 👈 改成 temp_report_dir
    
    results_dir.mkdir(exist_ok=True)
    

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
            cmd_allure = f"allure generate {results_dir} -o {temp_report_dir} --clean --single-file"
            subprocess.run(cmd_allure, shell=True)

            # 👈 在這裡進行加工與搬移
            generated_index = temp_report_dir / "index.html"
            if generated_index.exists():
                # A. 讀取內容並注入按鈕
                content = generated_index.read_text(encoding='utf-8')
                # 找到 run_test.py 中的這一段
                back_button_html = """
                <a href="../index.html" style="
                    position: fixed; 
                    bottom: 30px; 
                    right: 20px; 
                    padding: 10px 22px; 
                    background: #1e293b; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 50px; 
                    font-family: 'Noto Sans TC', 'Microsoft JhengHei', sans-serif; 
                    font-size: 14px; 
                    font-weight: 700; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2); 
                    z-index: 9999; 
                    transition: all 0.3s; 
                    display: flex; 
                    align-items: center; 
                    gap: 8px;
                " onmouseover="this.style.background='#0f172a'; this.style.transform='translateY(-3px)';" 
                onmouseout="this.style.background='#1e293b'; this.style.transform='translateY(0)';" 
                onclick="window.location.href='../index.html';">
                🏠 返回目錄
                </a>
                """
                
                new_content = content.replace("</body>", f"{back_button_html}</body>")
                generated_index.write_text(new_content, encoding='utf-8')

                # B. 加工完畢後，搬移到正式位置
                shutil.move(str(generated_index), str(final_report_file))
                print(f"✅ 報表已成功注入按鈕並搬移至: {final_report_file}")
                
                # C. 清理暫存資料夾
                shutil.rmtree(temp_report_dir)
            
            report_file = temp_report_dir / "index.html"
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
