#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界杯预测引擎 - 基于42维精进框架
数据源：模拟数据（可替换为真实API）
"""

import json
import random
from datetime import datetime, timedelta

# -------------------- 1. 模拟数据源（实际使用时替换为ESPN API）--------------------
def fetch_matches():
    """模拟获取今日比赛数据，返回比赛列表"""
    today = datetime.now().strftime("%Y-%m-%d")
    # 模拟两场比赛数据
    matches = [
        {
            "home": "挪威",
            "away": "科特迪瓦",
            "home_rank": 12,
            "away_rank": 40,
            "home_xg": 1.65,
            "away_xg": 0.95,
            "home_attack": 85,
            "home_defense": 70,
            "away_attack": 75,
            "away_defense": 80,
            "home_elo": 1850,
            "away_elo": 1680,
            "home_recent_goals": [2, 3, 1, 2, 4],
            "away_recent_goals": [1, 0, 2, 1, 1],
            "home_dependency": "high",      # high/medium/low
            "away_dependency": "medium",
            "referee_yellow_avg": 4.5,
            "temperature": 28,
            "altitude": 100,
            "h2h_recent": "1-0, 2-1",      # 近5年交锋
        },
        {
            "home": "法国",
            "away": "瑞典",
            "home_rank": 2,
            "away_rank": 23,
            "home_xg": 2.35,
            "away_xg": 0.75,
            "home_attack": 92,
            "home_defense": 88,
            "away_attack": 68,
            "away_defense": 72,
            "home_elo": 1980,
            "away_elo": 1720,
            "home_recent_goals": [3, 4, 2, 3, 5],
            "away_recent_goals": [1, 0, 2, 1, 0],
            "home_dependency": "low",
            "away_dependency": "high",
            "referee_yellow_avg": 3.2,
            "temperature": 22,
            "altitude": 50,
            "h2h_recent": "2-0, 1-1",
        }
    ]
    return matches

# -------------------- 2. 修正链路（简化版，展示你的框架）--------------------
def apply_corrections(match):
    """应用42维修正，返回修正后的xG和比分概率"""
    home_xg = match["home_xg"]
    away_xg = match["away_xg"]
    
    # 2.1 战术克制修正（基于分项评分）
    # 主队进攻 vs 客队防守
    if match["home_attack"] - match["away_defense"] > 10:
        home_xg += 0.2
    elif match["home_attack"] - match["away_defense"] < -5:
        home_xg -= 0.2
    
    # 客队进攻 vs 主队防守
    if match["away_attack"] - match["home_defense"] > 10:
        away_xg += 0.2
    elif match["away_attack"] - match["home_defense"] < -5:
        away_xg -= 0.2
    
    # 2.2 球星依赖度修正
    if match["home_dependency"] == "high":
        home_xg *= 0.9   # 若核心缺阵，下调10%
    if match["away_dependency"] == "high":
        away_xg *= 0.9
    
    # 2.3 裁判尺度修正（黄牌多→技术型球队受益）
    if match["referee_yellow_avg"] >= 5:
        home_xg += 0.15 if match["home_attack"] > 80 else 0
        away_xg += 0.15 if match["away_attack"] > 80 else 0
    
    # 2.4 高温修正
    if match["temperature"] > 30:
        home_xg *= 0.95
        away_xg *= 0.95
    
    # 2.5 回归修正（实际进球高于xG的回归）
    # 简化：直接取平均
    home_avg_goals = sum(match["home_recent_goals"]) / len(match["home_recent_goals"])
    away_avg_goals = sum(match["away_recent_goals"]) / len(match["away_recent_goals"])
    home_xg = (home_xg + home_avg_goals) / 2
    away_xg = (away_xg + away_avg_goals) / 2
    
    # 上限控制
    home_xg = min(max(home_xg, 0.2), 4.0)
    away_xg = min(max(away_xg, 0.2), 3.0)
    
    return round(home_xg, 2), round(away_xg, 2)

# -------------------- 3. 比分概率生成（泊松分布简化版）--------------------
def generate_score_prob(home_xg, away_xg):
    """基于修正xG生成比分概率（前6个）"""
    # 模拟泊松分布（简化：经验公式）
    scores = []
    # 常见比分集合
    possible = [(2,0), (1,0), (2,1), (1,1), (3,0), (0,0), (3,1), (0,1), (1,2)]
    # 计算概率（简易评分）
    for h, a in possible:
        # 概率与xG差值相关
        diff = abs(h - home_xg) + abs(a - away_xg)
        prob = max(0, 100 - diff * 25)  # 粗略转换
        scores.append({"home": h, "away": a, "prob": round(min(prob, 30), 1)})
    
    # 归一化（取前6个）
    scores.sort(key=lambda x: x["prob"], reverse=True)
    return scores[:6]

# -------------------- 4. 主函数 --------------------
def main():
    matches = fetch_matches()
    predictions = []
    
    for m in matches:
        home_xg, away_xg = apply_corrections(m)
        score_probs = generate_score_prob(home_xg, away_xg)
        
        # 判断胜负倾向
        if home_xg > away_xg + 0.3:
            result = "主胜"
        elif away_xg > home_xg + 0.3:
            result = "客胜"
        else:
            result = "平局"
        
        pred = {
            "home": m["home"],
            "away": m["away"],
            "home_xg": home_xg,
            "away_xg": away_xg,
            "result": result,
            "scores": score_probs,
            "confidence": "高" if abs(home_xg - away_xg) > 0.8 else "中",
            "risk": "中" if abs(home_xg - away_xg) < 0.5 else "低",
            "bts": "是" if (home_xg > 0.8 and away_xg > 0.6) else "否",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        predictions.append(pred)
    
    # 写入data.json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"matches": predictions, "last_updated": datetime.now().isoformat()}, f, indent=2, ensure_ascii=False)
    
    print("✅ 预测更新成功！")

if __name__ == "__main__":
    main()
