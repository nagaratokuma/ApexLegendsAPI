import streamlit as st
import requests
import sqlite3
import pandas as pd
from datetime import datetime

dbname = ('ApexPlayer.db')#データベース名.db拡張子で設定
conn = sqlite3.connect(dbname, isolation_level=None)#データベースを作成、自動コミット機能ON

cursor = conn.cursor() #カーソルオブジェクトを作成
# テーブル作成
sql = """CREATE TABLE IF NOT EXISTS PlayerSheet(name text primary key, count integer, level text, uid text, platform text, addDate text, updateDate text, rank text, currentState text)"""
cursor.execute(sql)
conn.commit()

base_url = "https://api.mozambiquehe.re/bridge?auth=e359f24291059eac45953627ccadd929&player="

# タイトル
st.title('ApexLegendsチーターデータベース')

# プレイヤーネームテキストボックス
player_name = st.text_input('OriginIDを入力してください')

#　プラットフォーム選択
platform = st.selectbox('プラットフォームを選択してください',('PC', 'PS4'))

# URL設定
url = base_url + player_name + "&platform=" + platform

# API呼び出しボタン
if st.button('API呼び出し'):
    res = requests.get(url).json()
    # resにErrorが含まれている場合
    if 'Error' in res:
        st.write('このプレイヤーはApexLegendsStatusで見つかりませんでした')
        uid = ''
        rank = ''
        currentState = ''
        level = ''
        
    else:
        uid = res['global']['uid']
        level = res['global']['level']
        st.write('Success')
        # テーブルにREPLACEでデータを1行追加
        # banされているとき
        if res['global']['bans']['isActive'] == 'true':
            currentState = "Banned"
        else:
            currentState = res['realtime']['currentStateAsText']
        
        # ランクが"Apex Predator" のとき
        if res['global']['rank']['rankName'] == "Apex Predator":
            rank = 'Predator' + " " + str(res['global']['rank']['ALStopInt'])
        else:
            rank = res['global']['rank']['rankName'] + " " + str(res['global']['rank']['rankDiv'])

    # すでにテーブルに存在するか確認
    sql = """SELECT * FROM PlayerSheet WHERE name = ?"""
    data = (player_name,)
    result = cursor.execute(sql, data)
    playerdata = result.fetchone()
    if playerdata is not None:
        #存在するとき
        count = playerdata[1] + 1
        sql = """UPDATE PlayerSheet SET count = ?, level = ?, updateDate = ?, rank = ?, currentState = ? WHERE name = ?"""
        data = (count, level, datetime.now().strftime('%Y/%m/%d %H:%M:%S'), rank, currentState, player_name)
        cursor.execute(sql, data)
        st.write('データを更新しました')
        #playerデータを表示
        sql = """SELECT * FROM PlayerSheet WHERE name = ?"""
        data = (player_name,)
        result_df = pd.read_sql(sql, conn, params=data)
        st.dataframe(result_df)
        
    else:
        #存在しないとき
        sql = """REPLACE INTO PlayerSheet VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        data = (player_name, 1, level, uid, platform, datetime.now().strftime('%Y/%m/%d %H:%M:%S'), datetime.now().strftime('%Y/%m/%d %H:%M:%S'), rank, currentState)
        cursor.execute(sql, data)
        st.write('データベースに新規登録しました')
    
        
        
    #(isExist text, name text primary key, platform text, addDate datetime, updateDate datetime, lastLiveDate datetime, rank text, currentState text)

    # データベースからデータを取得
    sql = """SELECT * FROM PlayerSheet"""
    df = pd.read_sql(sql, conn)
    st.dataframe(df)



#作業完了したらDB接続を閉じる
conn.close()