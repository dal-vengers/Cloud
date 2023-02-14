import os
import boto3
from PIL import Image, ImageDraw, ImageFont
import PIL
import sys
import logging
import pymysql
import datetime
#import json

def lambda_handler(event, context):
    records = event['Records']

    if records :
        regist_num = records[0]['Sns']['Message']

    conn = pymysql.connect(host="project.cgx0gwgzdjyz.us-east-1.rds.amazonaws.com", user="admin", password="cloud0822", db="info_DB")
    curs = conn.cursor()
    sql = "select walk_info.walk, walk_info.walk_start_time, walk_info.total_walk_time, walk_info.total_num_steps, walk_info.distance, walk_info.regist_num, dog_info.regist_num from walk_info, dog_info \
    where walk_info.regist_num = '{}' and dog_info.regist_num = '{}'".format(regist_num, regist_num)

    #[0] index [1] 산책 시작 시간 [2] 산책 토탈 시간 [3] 걸음수 [4] 거리 [5] 개등록번호

    curs.execute(sql)
    rows = curs.fetchall()

    result = []
    #rows 값 result 배열에 삽입
    for row in rows:
        result.append(row)

    day = result[-1][1].weekday() #오늘 산책 요일(0=월요일, 3=목요일, 6=일요일)
    today = result[-1][1].date() #오늘 산책 date

    sum_distance = []
    for i in range(len(rows)):
        days = result[i][1].date() #받아온 산책data의 date(today랑 같은 주인지 비교)
        if day == 0 and today == days: #today가 월요일, 받아온 date랑 today가 같으면
            sum_distance.append(result[i][4])
        elif day == 1:
            monday = today-datetime.timedelta(days=1)
            sunday = today+datetime.timedelta(days=5)
            if monday<=days and sunday>=days:
                sum_distance.append(result[i][4])
        elif day == 2:
            monday = today-datetime.timedelta(days=2)
            sunday = today+datetime.timedelta(days=4)
            if monday<=days and sunday>=days:
                sum_distance.append(result[i][4])
        elif day == 3:
            monday = today-datetime.timedelta(days=3)
            sunday = today+datetime.timedelta(days=3)
            if monday<=days and sunday>=days:
                sum_distance.append(result[i][4])
        elif day == 4:
            monday = today-datetime.timedelta(days=4)
            sunday = today+datetime.timedelta(days=2)
            if monday<=days and sunday>=days:
                sum_distance.append(result[i][4])
        elif day == 5:
            monday = today-datetime.timedelta(days=5)
            sunday = today+datetime.timedelta(days=1)
            if monday<=days and sunday>=days:
                sum_distance.append(result[i][4])
        elif day == 6:
            monday = today-datetime.timedelta(days=6)
            if monday<=days:
                sum_distance.append(result[i][4])

    sum_distances = round(sum(sum_distance),1)

    walk_start_time = result[-1][1].strftime('%Y-%m-%d %H:%M:%S') #오늘 산책 시작 시간(초포함 - 폴더명용)
    walk_start_time2 = result[-1][1].strftime('%Y-%m-%d %H:%M') #오늘 산책 시작 시간
    walk_time = result[-1][2] #오늘 산책 시간
    num_steps = result[-1][3] #오늘 산책 걸음수
    today_distance = result[-1][4] #오늘 산책 거리
    regist = result[-1][5] #강아지 등록번호
    conn.close()

    W, H = (250, 400)

    # 1) logo img
    s3 = boto3.resource('s3')
    s3.Bucket(os.environ['BUCKET_NAME']).download_file('fonts/font.otf', '/tmp/font.otf')
    s3.Bucket(os.environ['BUCKET_NAME']).download_file('fonts/ROKAF_Bold.otf', '/tmp/ROKAF_Medium.otf')
    s3.Bucket(os.environ['BUCKET_NAME']).download_file('fonts/ROKAF_Bold.otf', '/tmp/ROKAF_Bold.otf')

    otf = '/tmp/font.otf' #font
    otf2 = '/tmp/ROKAF_Medium.otf'
    otf3 = '/tmp/ROKAF_Bold.otf'

    s3.Bucket(os.environ['BUCKET_NAME']).download_file('dogs/'+str(regist_num)+'/dogface.png', '/tmp/dogface.png')
    dogface = Image.open('/tmp/dogface.png').convert('RGBA')
    dogface_size = dogface.size
    print(dogface.size)

    if dogface_size[0]>dogface_size[1]:
        c_dogface = dogface.crop(((dogface_size[0]-dogface_size[1])/2, 0, (dogface_size[0]-dogface_size[1])/2+dogface_size[1], dogface_size[1]))
    else:
        c_dogface = dogface.crop((0, (dogface_size[1]-dogface_size[0])/2 , dogface_size[0], (dogface_size[1]-dogface_size[0])/2+dogface_size[0]))

    print("cropimage size : ", c_dogface.size)
    r_dogface = c_dogface.resize((45,45))

    # 3) merge
    img = Image.new('RGB', (W, H), (255, 255, 235))
    img.paste(r_dogface, (175, 35), r_dogface)
    draw = ImageDraw.Draw(img)

    # 4) draw
    font_s = ImageFont.truetype(otf, 9)
    font_m = ImageFont.truetype(otf2, 15)
    font_l = ImageFont.truetype(otf3, 23)

    draw.text((38, 35), walk_start_time2, fill='#585858', font=font_s)
    draw.text((35, 50), "오늘의 산책", fill='#000', font=font_l)
    draw.text((28, 65), "_________________", fill='#000', font=font_m)

    draw.text((40, 100), f'거리', fill='#585858', font=font_s)
    draw.text((145, 100), f'이번주 산책 거리', fill='#585858', font=font_s)
    draw.text((40, 115), f'{today_distance} Km', fill='#000', font=font_m)
    draw.text((145, 115), f'{sum_distances} Km', fill='#000', font=font_m)

    draw.text((40, 160), f'걸음수', fill='#585858', font=font_s)
    draw.text((145, 160), f'산책 시간', fill='#585858', font=font_s)
    draw.text((40, 177), f'{num_steps} steps', fill='#000', font=font_m)
    draw.text((145, 177), f'{walk_time} min', fill='#000', font=font_m)
    draw.rectangle((20, 220, 228, 360), fill='#f0f0f0')

    img.save(f'/tmp/signed.jpg', quality=100)

    key = f'walk_info_image/{regist}/walkimage.jpg'
    s3.meta.client.upload_file('/tmp/signed.jpg', os.environ['BUCKET_NAME'], key, ExtraArgs={'ContentType':'image/jpeg'})
    
    return {
        'statusCode': 200,
        'event': event,
        #'item' : item
        'distance' : sum_distances
    }
