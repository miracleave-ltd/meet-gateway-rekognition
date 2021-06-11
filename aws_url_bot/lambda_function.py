import json
import boto3
import logging
import os
import urllib.request
import urllib.parse
import name_map

##環境変数の宣言
LINE_CHANNEL_ACCESS_TOKEN  = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

rekognition = boto3.client('rekognition')

def lambda_handler(event, context):

    for message_event in json.loads(event['body'])['events']:
        ###########
        ## AWS処理
        ###########
        
        aws_url = 'https://AWS画像解析URL'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + LINE_CHANNEL_ACCESS_TOKEN
        }

        # 画像ID取得
        gazo_id =  message_event['message']['id']
        # AWS画像解析APIへリクエスト
        geturl = "https://api-data.line.me/v2/bot/message/" + gazo_id + "/content"
        getmethod = "GET"
        request = urllib.request.Request(geturl, method=getmethod, headers=headers)
        
        with urllib.request.urlopen(request) as res:
            body1 = res.read()

            detect = rekognition.detect_labels(
                Image={
                    "Bytes": body1
                }
            )
            labels = detect['Labels']
            
            search_condition = None
            
            for value in labels:
                print(value)
                if value['Name'] == 'Monitor' or value['Name'] == 'Display':
                    search_condition = name_map.MONITOR_DISPLAY
                    break
                
                elif value['Name'] == 'Sneaker' or value['Name'] == 'Shoe':
                    search_condition = name_map.SNEAKER_SHOE
                    break
                
                elif value['Name'] == 'Pc' or value['Name'] == 'Laptop':
                    search_condition = name_map.PC_LAPTOP
                    break
                elif value['Name'] == 'Bag'or value['Name'] == 'Tote Bag':
                    search_condition = name_map.BAG_TOTEBAG
                    break
                elif value['Name'] == 'Chair':
                    search_condition = name_map.CHAIR
            
            ###########
            ## LINE処理
            ###########
            line_url = 'https://api.line.me/v2/bot/message/reply'
            line_body = {
                'replyToken': message_event['replyToken'],
                'messages': [
                    {
                        "type": "text",
                        "text": "https://www.amazon.co.jp/s?k="+urllib.parse.quote(' '.join(search_condition))+"&ref=nb_sb_noss_1",
                    }
                ]
            }

            line_req = urllib.request.Request(line_url, data=json.dumps(line_body).encode('utf-8'), method='POST', headers=headers)
            with urllib.request.urlopen(line_req) as res:
                logging.info(res.read().decode("utf-8"))

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }