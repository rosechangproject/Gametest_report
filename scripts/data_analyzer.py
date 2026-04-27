"""
資料分析核心模組 - 負責資料抓取與風險勝率運算
"""
import os
import json
import urllib.request
from datetime import datetime
from config import API_CONFIG, CHASING_TYPES, COLUMN_MAP, RISK_THRESHOLD_WR, MIN_SAMPLE_SIZE

def fetch_raw_data(key: str, url: str) -> list:
    """從 API 或本地備份獲取原始資料"""
    print(f"[FETCH] 正在獲取 {key} 數據...")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode('utf-8'))
            rows = data.get('rows', [])
            print(f"[SUCCESS] {key} API 抓取成功 ({len(rows)} 筆)")
            return rows
    except Exception as e:
        print(f"[WARNING] {key} API 連線失敗 ({e})，嘗試加載本地備份...")
        local_file = f"{key}.json"
        if os.path.exists(local_file):
            with open(local_file, 'r', encoding='utf-8') as f:
                return json.load(f).get('rows', [])
    return []

def analyze_risk_data(rows_wl: list, rows_mo: list):
    """
    執行三級風險分析判定
    返回: (詳細翻譯數據, 摘要報告, 異常明細, 測試期間, 風險分佈計數)
    """
    print(f"[PROCESS] 正在啟動風險分析引擎 (房型門檻: {CHASING_TYPES})...")
    
    # 1. 建立錢包餘額對照表 (優化查詢效能)
    mo_dict = {}
    for r in rows_mo:
        acc = r.get('account')
        g_no = r.get('gameNo') or r.get('gameUserNO')
        if acc and g_no:
            mo_dict[f"{acc}_{g_no}"] = r.get('money', '0')

    # 2. 統計各遊戲在「殺局房型」下的勝率
    chasing_stats = {}
    for r in rows_wl:
        g_name = r.get('gameName', 'Unknown')
        r_type = r.get('roomType')
        
        if r_type in CHASING_TYPES:
            if g_name not in chasing_stats:
                chasing_stats[g_name] = {'total': 0, 'wins': 0}
            
            chasing_stats[g_name]['total'] += 1
            try:
                # 損益清洗與贏錢判定
                p = float(str(r.get('profit', '0')).replace(',', ''))
                if p > 0:
                    chasing_stats[g_name]['wins'] += 1
            except: pass

    # 3. 匯總分析與翻譯
    final_rows = []
    abnormal_details = []
    summary_report = []
    risk_dist = {"異常數據": 0, "正常數據": 0, "樣本不足": 0}
    all_times = []

    # 處理勝率與判定
    for g_name, stat in chasing_stats.items():
        total = stat['total']
        wins = stat['wins']
        wr = wins / total if total > 0 else 0
        
        # --- 三級判定邏輯 ---
        if total < MIN_SAMPLE_SIZE:
            status = "樣本不足"
        elif wr > RISK_THRESHOLD_WR:
            status = "異常"
        else:
            status = "正常"
            
        dist_key = status if status == "樣本不足" else status + "數據"
        risk_dist[dist_key] += 1
        
        summary_report.append({
            "遊戲名稱": g_name, 
            "追殺總局數": total, 
            "異常局數": wins, 
            "勝率": wr,
            "殺局贏錢比例": f"{wr:.2%}", 
            "分析結果": status
        })
        
        # 打印終端狀態 (簡潔化輸出)
        prefix = "[SAMPLE]" if status == "樣本不足" else ("[ALERT]" if status == "異常" else "[OK]")
        print(f"  {prefix} {g_name:12} | 總計: {total:4} | 勝率: {wr:7.2%} | 判定: {status}")

    # 4. 生成明細與翻譯
    for r in rows_wl:
        g_name = r.get('gameName', 'Unknown')
        r_type = r.get('roomType')
        stat = chasing_stats.get(g_name, {'total': 0, 'wins': 0})
        total_wr = stat['wins'] / stat['total'] if stat['total'] > 0 else 0
        
        # 欄位翻譯
        trans = {COLUMN_MAP.get(k, k): v for k, v in r.items()}
        trans['殺局贏錢比例'] = f"{total_wr:.2%}"
        final_rows.append(trans)

        # 擷取異常明細 (殺局房 + 勝率異常 + 有贏錢)
        try:
            p_val = float(str(trans.get('損益', '0')).replace(',', ''))
            if (total_wr > RISK_THRESHOLD_WR and r_type in CHASING_TYPES and p_val > 0 and stat['total'] >= MIN_SAMPLE_SIZE):
                abnormal_details.append(trans)
        except: pass

        t = r.get('gameEndTime')
        if t: all_times.append(t)

    # 5. 計算測試期間
    test_period = "無時間數據"
    if all_times:
        try:
            cleaned_times = sorted([t for t in all_times if len(str(t)) > 10])
            test_period = f"{cleaned_times[0]} ~ {cleaned_times[-1]}"
        except: pass

    return final_rows, summary_report, abnormal_details, test_period, risk_dist
