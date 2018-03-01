from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import datetime

from flask import Flask
from flask import request
from flask import make_response, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import pandas as pd
from gspread_dataframe import get_as_dataframe

import requests


# Flask app should start in global layout
app = Flask(__name__)



@app.route('/webhook', methods=['POST','GET'])
def webhook():
	
	GHkit_ID=['p27bw7yga4','52s6t8fd8b']
	
	now=datetime.datetime.now()
	event_date= str(now.year)+"年"+str(now.month)+"月"+str(now.day)+"日"
	speak_date="今日"
	scope = ['https://www.googleapis.com/auth/drive']
	
     #ダウンロードしたjsonファイルを同じフォルダに格納して指定する
	credentials = ServiceAccountCredentials.from_json_keyfile_name('My First Project-fc3744a8d618.json', scope)
	gc = gspread.authorize(credentials)
	
	# # 共有設定したスプレッドシートの名前を指定する
	worksheet = gc.open("Event_Info").sheet1

	#dataframeにする
	df = get_as_dataframe(worksheet, parse_dates=False,index=None)


	#TODO ここから下はdataframeとして操作
	text=""


	df_filtered=df[df['日付'].isin([event_date])]
	length=len(df_filtered.index)

	#指定した日付のピタリ賞があった場合
	if length>0:
		titles=df_filtered['イベント名'].values.tolist()
		places=df_filtered['場所'].values.tolist()
		timestamps=df_filtered['時間'].values.tolist()
		regions=df_filtered['地区'].values.tolist()
		text='おはようございます。'+speak_date+'は、'

		for i in range(length):
			if i>0:
				text=text+'また、'
			if timestamps[i]=='-':
				text=text+places[i] +"で"+titles[i]+"があります。"
			else:
				text=text+places[i] +"で"+timestamps[i]+"から"+titles[i]+"があります。"

	#なかった場合、一番近いものを持ってくる
	else:
		Founded=False
		date_list=df['日付'].values.tolist()
		dt_format_query=datetime.datetime.strptime(event_date,'%Y年%m月%d日')

		for j in range(1,len(date_list)):
			#datetimeに変換
			dt_format=datetime.datetime.strptime(date_list[j],'%Y年%m月%d日')
			if dt_format_query<dt_format:
				df_filtered=df[df['日付'].isin([date_list[j]])]
				Founded=True
				break
		if Founded:
			length=len(df_filtered.index)
			titles=df_filtered['イベント名'].values.tolist()
			places=df_filtered['場所'].values.tolist()
			timestamps=df_filtered['時間'].values.tolist()
			regions=df_filtered['地区'].values.tolist()
			text='おはようございます。今日はイベントはありません。近い日にちだと、'+str(date_list[j]).replace('2018年','')+'に、'

			for i in range(length):
				if i>0:
					text=text+'また、'
				if timestamps[i]=='-':
					text=text+places[i] +"で"+titles[i]+"があります。"
				else:
					text=text+places[i] +"で"+timestamps[i]+"から"+titles[i]+"があります。"

		else:
			text='おはようございます。近くでイベントは特にありませんが、'
			
	url='http://ifttt.ghkit.jp/'
	headers = {"Content-Type" : "application/json"}
	text=text+'外に出かけてみては、いかがでしょうか。'
	
	r=[]
	
	for j in range(len(GHkit_ID)):
	#GHkitにPOST

		text_post=GHkit_ID[j]+text
		text_post='"'+text_post+'"'
		obj={"message" : text_post}
		json_data = json.dumps(obj).encode("utf-8")

		# httpリクエストを準備してPOST
		r.append(requests.post(url, data=json_data, headers=headers))

	return r


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
