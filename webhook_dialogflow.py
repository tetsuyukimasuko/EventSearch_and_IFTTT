from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import urllib
import requests

import json
import os
import datetime

from flask import Flask
from flask import request
from flask import make_response, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
	now=datetime.datetime.now()
	event_date= str(now.year)+"年"+str(now.month)+"月"+str(now.day)+"日"
	speak_date="今日"
	scope = ['https://www.googleapis.com/auth/drive']
	
    #ダウンロードしたjsonファイルを同じフォルダに格納して指定する
	credentials = ServiceAccountCredentials.from_json_keyfile_name('My First Project-fc3744a8d618.json', scope)
	gc = gspread.authorize(credentials)
    # # 共有設定したスプレッドシートの名前を指定する
	worksheet = gc.open("Event_Info").sheet1
	text=""
	cell = worksheet.findall(event_date)	
	
	if len(cell) > 0:
		for cl in cell:
			
			title=str(worksheet.cell(cl.row,1).value)
			place=str(worksheet.cell(cl.row,4).value)
			timestamp=str(worksheet.cell(cl.row,3).value)
			if timestamp=="-":
				tmp=place +"で"+title+"があります。"
			else:
				tmp=place +"で"+timestamp+"から"+title+"があります。"
			
			if text!="":
				text += "また、"+ tmp

			else:
				text = speak_date + "は、" +tmp

	else:
		text=speak_date+'のイベントは見つかりませんでした。'
	
	#IFTTTにPOST
	url = "https://maker.ifttt.com/trigger/Event_Info/with/key/c7O3t4lu4Gb6Y7qA9_19HzK0sD9wiqt6L99Ltti_TAE" 
	headers = {"Content-Type" : "application/json"}
	text='p27bw7yga4'+text
	text='"'+text+'"'
	text='"message" : ' + text
	text='{'+text+'}'
	# PythonオブジェクトをJSONに変換する
	obj = {"value1" : text }
	json_data = json.dumps(obj).encode("utf-8")

	# httpリクエストを準備してPOST
	r = requests.post(url, data=json_data, headers=headers)
		
	return r


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
