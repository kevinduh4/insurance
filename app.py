import pandas as pd
from pytrends.request import TrendReq
from snownlp import SnowNLP
from flask import Flask, jsonify
import time
import os
import subprocess

app = Flask(__name__)

# 設定 Google Trends 參數
def get_trends_data(keywords, timeframe='today 5-y', geo='TW'):
    pytrends = TrendReq()
    pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)
    data = pytrends.interest_over_time()
    if 'isPartial' in data.columns:
        data = data.drop(columns=['isPartial'])
    return data

# 使用 SnowNLP 進行情緒分析
def analyze_sentiment(text):
    return SnowNLP(text).sentiments  # 0(負面) 到 1(正面)

@app.route("/run_crawler", methods=["GET"])
def run_crawler():
    insurance_companies = ["國泰人壽", "富邦人壽", "南山人壽", "新光人壽"]
    trend_data = get_trends_data(insurance_companies)
    trend_file = "google_trends_insurance.csv"
    trend_data.to_csv(trend_file)
    
    # 假設已爬取 PTT 或 Google Maps 評論
    reviews = [
        "這家保險公司賠償很快，服務態度很好",
        "理賠超慢，完全爛透了",
        "保費便宜，但保障普通，還行吧",
    ]

    sentiments = [analyze_sentiment(review) for review in reviews]
    review_df = pd.DataFrame({"review": reviews, "sentiment": sentiments})
    review_file = "insurance_sentiment_analysis.csv"
    review_df.to_csv(review_file, index=False)
    
    # 推送 CSV 到 GitHub
    repo_url = "https://github.com/kevinduh4/insurance.git"  # 修改為你的 GitHub Repo
    subprocess.run(["git", "config", "--global", "user.email", "your-email@example.com"])
    subprocess.run(["git", "config", "--global", "user.name", "your-github-username"])
    subprocess.run(["git", "add", trend_file, review_file])
    subprocess.run(["git", "commit", "-m", "更新爬取的 Google Trends 和情緒分析數據"])
    subprocess.run(["git", "push", repo_url, "main"])
    
    return jsonify({"message": "爬蟲執行完成，數據已存入 CSV 並推送到 GitHub！"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
