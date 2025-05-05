#!/usr/bin/env python
# coding: utf-8

# In[14]:


import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials

def get_dlsite_ranking_selenium(url, label):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    items = soup.select("li[class^='n-work']")[:10]
    data = []

    for item in items:
        title = item.select_one("span.title").get_text(strip=True)
        circle = item.select_one("span.maker_name").get_text(strip=True)
        link = item.select_one("a")["href"]
        work_id = re.search(r"/RJ(\d+)", link)
        work_id = "RJ" + work_id.group(1) if work_id else "不明"

        try:
            seiyu = item.select_one("span.cast").get_text(strip=True)
        except:
            seiyu = "不明"

        try:
            genre = item.select_one("span.genre").get_text(strip=True)
        except:
            genre = "不明"

        try:
            price = item.select_one("span.price").get_text(strip=True)
        except:
            price = "不明"

        data.append({
            "区分": label,
            "管理ID": work_id,
            "タイトル": title,
            "作品ページURL": f"https://www.dlsite.com{link}",
            "声優名": seiyu,
            "サークル名": circle,
            "ジャンル": genre,
            "価格": price
        })

    return data

# 取得対象URL
home_url = "https://www.dlsite.com/home/ranking/=/term/7d/work_type/voice"
r18_url = "https://www.dlsite.com/maniax/ranking/=/term/7d/work_type/voice"

# データ取得
home_data = get_dlsite_ranking_selenium(home_url, "全年齢")
r18_data = get_dlsite_ranking_selenium(r18_url, "R18")

# 結合・データフレーム化
df = pd.DataFrame(home_data + r18_data)

# Googleスプレッドシート書き出し設定
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('your_service_account.json', scope)
gc = gspread.authorize(creds)

spreadsheet = gc.create("DLsiteランキング出力")
spreadsheet.share('', perm_type='anyone', role='writer')  # 公開設定（必要なら編集）

worksheet = spreadsheet.get_worksheet(0)
worksheet.update_title("ランキングデータ")

# スプレッドシートに書き込み
set_with_dataframe(worksheet, df)
print("✅ スプレッドシートに出力完了！")
print(spreadsheet.url)


# In[ ]:




