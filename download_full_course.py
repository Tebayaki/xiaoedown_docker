import requests
import urllib.parse
import json
import xiaoedown

app_id = ""
resource_id = ""
course_id = ""
user_id = ""
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
cookie = ""
page_size = 50

# 获取章节列表
params = {
'bizData[app_id]': app_id,
'bizData[resource_id]': resource_id,
'bizData[course_id]': course_id,
'bizData[p_id]': '0',
'bizData[order]': 'asc',
'bizData[page]': '1',
'bizData[page_size]': page_size,
'bizData[sub_course_id]': '',
}

api_url = f"https://{app_id}.xet.citv.cn/xe.course.business.avoidlogin.e_course.horizontal.resource_catalog_list.get/1.0.0"
url = api_url + "?" + urllib.parse.urlencode(params)

payload = {}

headers = {
  'User-Agent': user_agent,
  'Cookie': cookie,
}

response = requests.request("POST", url, headers=headers, data=payload)
course = []
if response.ok:
    res = response.json()
    for chapter in res['data']['list']:
        course.append({'title': chapter['chapter_title'], 'id': chapter['chapter_id']})

i = 1
for chapter in course:
    resource_id = chapter['id']
    # 获取play_sign
    params = {
        'bizData[resource_id]': resource_id,
        'bizData[product_id]': course_id,
        'bizData[opr_sys]': 'Win32',
    }
    payload = {}
    headers = {
        'User-Agent': user_agent,
        'Cookie': cookie,
    }
    api_url = f"https://{app_id}.xet.citv.cn/xe.course.business.video.detail_info.get/2.0.0"
    url = api_url + "?" + urllib.parse.urlencode(params)

    course = []
    response = requests.request("POST", url, headers=headers, data=payload)
    play_sign = response.json()['data']['video_info']['play_sign']

    # 获取视频url
    url = f"https://{app_id}.xet.citv.cn/xe.material-center.play/getPlayUrl"

    payload = json.dumps({
        "org_app_id": app_id,
        "app_id": app_id,
        "user_id": user_id,
        "play_sign": [
            play_sign
        ],
        "play_line": "A",
        "opr_sys": "Win32"
    })

    headers = {
        'User-Agent': user_agent,
        'Cookie': cookie,
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    player = response.json()['data'][play_sign]
    play_url = player['play_list'][player['default_play']]['play_url']
    chapter['play_url'] = play_url
    print(chapter['title'], play_url, sep='\t')

    xiaoedown.main(play_url, f"{'%03d' % i}-{chapter['title']}.mp4")
    i = i + 1