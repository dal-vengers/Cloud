import recommend as rec
import urllib.parse

def lambda_handler(event, context):
    # 사용자 좌표
    user_coordinate= (37.5119303471109, 127.03808107256)
    lat = user_coordinate[0]
    lng = user_coordinate[1]
    
    # 장소 / 애견카페 혹은 애견동반카페
    type = urllib.parse.unquote(event.get('type'))
    # 좋아하는 카테고리
    like = event.get("category")
    # 원하는 거리
    distance = float(event.get("distance"))

    # 추천 시스템 알고리즘 함수 from .recommend import recommend
    result = rec.recom(type , like, distance, lat, lng)
                    #   장소,  카테고리,  거리, 좌표

    return result