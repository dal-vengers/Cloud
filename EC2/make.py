import os
import time
import folium
from boto3.dynamodb.conditions import Key, Attr
import pandas as pd
import boto3
import pymysql
import json
import datetime
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def open_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.delete_all_cookies()
    driver.set_page_load_timeout(10)
    driver.set_script_timeout(10)
    driver.maximize_window()

    return driver

def json_default(value):
    if isinstance(value, datetime.date):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    raise TypeError('not JSON serializable')


conn = pymysql.connect(host='', user='', password='', db='')

curs = conn.cursor()

sql = "SELECT walk_start_time, walk_end_time FROM walk_info"

curs.execute(sql)

res = curs.fetchall()

conn.close()

dynamodb = boto3.resource('dynamodb', region_name='', aws_access_key_id='',aws_secret_access_key='')

table = dynamodb.Table('sensor')

response = table.scan(
    FilterExpression = Attr ( 'device_name' ) . eq ( '2' )
)

show = response['Items']
lines = pd.DataFrame(show)

lines = lines.sort_values(by=['date'], axis=0, ascending = True)
lines = lines.reset_index(drop=True)

walk_start_time = json.dumps(res[-1][0], default=json_default)
walk_end_time = json.dumps(res[-1][1], default=json_default)

lines = lines[lines['date'] > walk_start_time]
lines = lines[lines['date'] < walk_end_time]

cen_lat = (float(max(lines['lat'])) + float(min(lines['lat'])))/2
cen_lon = (float(max(lines['lon'])) + float(min(lines['lon'])))/2

center = [cen_lat, cen_lon]

line_coor = []

for i in range(len(lines)-1):
  coor = [float(lines.iloc[i]['lat']), float(lines.iloc[i]['lon'])]
  line_coor.append(coor)

m = folium.Map(location=center,
    zoom_start=16.5
)

folium.PolyLine(
    locations = line_coor,
    tooltip = 'PolyLine'
).add_to(m)

fn='index.html'
tmpurl='file://{path}/{mapfile}'.format(path=os.getcwd(),mapfile=fn)
m.save(fn)

driver = open_driver()
driver.get(tmpurl)

driver.save_screenshot('map.png')
driver.quit()


s3 = boto3.resource('s3', aws_access_key_id='',aws_secret_access_key='')

key = f'image/3/walkimage.jpg'
s3.meta.client.upload_file('map.png', 'pjt4image-newbucket', key)
