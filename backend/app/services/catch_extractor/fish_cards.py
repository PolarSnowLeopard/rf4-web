import os
import json
import requests
import base64
from services.catch_extractor.utils import load_image_from_file
import dotenv
from services.catch_extractor.utils import get_file_content_as_base64

dotenv.load_dotenv()

def get_fish_cards_result(image_url: str = None, image_path: str = None):
    if image_url:
        image_type = "url"
    elif image_path:
        image_type = "local"
    else:
        raise ValueError("image_url or image_path is required")

    if image_type == "local":
        base64_image = get_file_content_as_base64(image_path)

    url = "https://serverless.roboflow.com/infer/workflows/polarsnowleopard-jwqgz/detect-count-and-visualize"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "api_key": os.getenv("ROBOFLOW_API_KEY"),
        "inputs": {
            "image": {
                "type": image_type, 
                "value": image_url if image_type == "url" else base64_image
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    return result

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))

    OUTPUT_PATH = 'fish_cards_result.json'
    OUTPUT_IMAGE_PATH = 'fish_cards_image.jpg'

    # 直接从本地文件读取图片
    image_path = os.path.join(current_dir, 'main_result.png')
    # image = cv2.imread(image_path)
    
    # if image is None:
    #     print(f"无法读取图像: {image_path}")
    #     exit(1)
        
    # # 将图像转换为jpg并编码为base64字符串
    # _, buffer = cv2.imencode('.jpg', image)
    # base64_image = base64.b64encode(buffer).decode('utf-8')

    # base64_image = get_file_content_as_base64(image_path)
    
    # 调用API
    result = get_fish_cards_result(image_path=image_path)
    print(result)

    # 如果API返回正确结果，处理输出
    if 'outputs' in result and len(result['outputs']) > 0:
        image_base64 = result['outputs'][0]['output_image']['value']
        image_data = base64.b64decode(image_base64)
        
        # 保存图片
        with open(os.path.join(current_dir, OUTPUT_IMAGE_PATH), 'wb') as f:
            f.write(image_data)
            
        # 保存JSON结果
        with open(os.path.join(current_dir, OUTPUT_PATH), 'w') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)