import base64
import urllib
import requests
import os
import json
import dotenv

dotenv.load_dotenv()

API_KEY = os.getenv("BAIDU_API_KEY")
SECRET_KEY = os.getenv("BAIDU_SECRET_KEY")

def get_ocr_result(image_url: str = None, image_path: str = None):
    if image_url:
        image_type = "url"
    elif image_path:
        image_type = "local"
    else:
        raise ValueError("image_url or image_path is required")

    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate?access_token=" + get_access_token()
    if image_type == "url":
        payload='url=' + image_url + '&detect_direction=false&vertexes_location=false&paragraph=false&probability=false&char_probability=false&multidirectional_recognize=false'
    elif image_type == "local":
        payload = 'image=' + get_file_content_as_base64(image_path, True)
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))
    
    return response.json()

def get_file_content_as_base64(path, urlencoded=False):
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded 
    :return: base64编码信息
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

if __name__ == '__main__':
    result = get_ocr_result(image_path='/home/ubuntu/github/rf4/app/services/catch_extractor/main_result.png')
    print(result)
    print(get_access_token())
