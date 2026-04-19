import os
import json
from PIL import Image
from services.catch_extractor.fish_cards import get_fish_cards_result
from services.catch_extractor.roboflow_format import convert_yolo_to_standard
from services.catch_extractor.get_ocr_result import get_ocr_result
from services.catch_extractor.utils import (BoundingBox, 
                   load_image_from_url, 
                   load_image_from_file, 
                   save_image_to_file, 
                   draw_bounding_boxes_on_image,
                   get_field_from_word)

current_dir = os.path.dirname(os.path.abspath(__file__))

def extract_fishes(image_url: str = None, image_path: str = None) -> tuple[Image.Image, list[list[str]]]:
    """
    提取图片中的鱼
    :param image_url: 图片url
    :param image_path: 图片路径，绝对路径
    :return: 图片和fishes
    """
    if image_url:
        image_type = "url"
    elif image_path:
        image_type = "local"
    else:
        raise ValueError("image_url or image_path is required")
    
    # 0. 加载图片
    if image_type == "url":
        image = load_image_from_url(image_url)
    elif image_type == "local":
        image = load_image_from_file(image_path)
    
    # 1. 调用roboflow目标检测工作流，识别fish_cards
    if image_type == "url":
        fish_cards_result = get_fish_cards_result(image_url=image_url)
    elif image_type == "local":
        fish_cards_result = get_fish_cards_result(image_path=image_path)

    # 2. 调用baidu_ocr_api，识别文字
    if image_type == "url":
        ocr_result = get_ocr_result(image_url=image_url)
    elif image_type == "local":
        ocr_result = get_ocr_result(image_path=image_path)

    # 3. 将roboflow结果转换为标准格式
    stardard_fish_cards_results = convert_yolo_to_standard(fish_cards_result)

    # 4. 转化为BoundingBox列表
    fish_cards = []
    for item in stardard_fish_cards_results['result']:
        location = item['location']
        left, top, width, height = location['left'], location['top'], location['width'], location['height']
        fish_cards.append(BoundingBox(left, top, width, height, False))

    # 5. 解析ocr结果，获取文字信息
    words_cards = []
    # 只从鱼市出售页面的列表中提取文字
    unmarked_bounding = BoundingBox(410, 126, 1920 - 410, 1080 - 126, False)
    for item in ocr_result['words_result']:
        location = item['location']
        left, top, width, height = location['left'], location['top'], location['width'], location['height']
        item['BoundingBox'] = BoundingBox(left, top, width, height, False, item['words'])
        if unmarked_bounding.is_overlapping(item['BoundingBox']):
            # 如果和上一个item的BoundingBox重叠，则合并
            if words_cards and words_cards[-1]['BoundingBox'].is_overlapping(item['BoundingBox']):
                words_cards[-1]['BoundingBox'] += item['BoundingBox']
                words_cards[-1]['words'] += item['words']
            else:
                words_cards.append(item)

    # 6. 对于每个word_card，匹配与其重合的fish_card
    for i, word_card in enumerate(words_cards):
        for j, fish_card in enumerate(fish_cards):
            if word_card['BoundingBox'].is_overlapping(fish_card):
                words_cards[i]['fish_card_index'] = j
                break

    # 7 按每个fish整理word_cards
    fishes = []
    for i in range(len(fish_cards)):
        fish = dict()
        for word_card in words_cards:
            # 排除误识别的字块，如"√"和"×"
            if len(word_card['words']) < 2:
                continue
            fish_card_index = word_card.get('fish_card_index', None)
            if fish_card_index is not None and fish_card_index == i:
                item = get_field_from_word(word_card['words'])
                field_name, field_value = item['key'], item['value']
                fish[field_name] = field_value
        if len(fish) > 0:
            fishes.append([fish.get('time_percentage', ''), 
                           fish.get('fish_name', ''), 
                           fish.get('weight', ''), 
                           fish.get('price', '')])

    # 8 保存fishes
    # with open(os.path.join(current_dir, 'fishes.json'), 'w') as f:
    #     json.dump(fishes, f, indent=4, ensure_ascii=False)
    print(json.dumps(fishes, indent=4, ensure_ascii=False))

    # 9 绘制结果
    draw_bounding_boxes_on_image(image, fish_cards)
    draw_bounding_boxes_on_image(image, [wc['BoundingBox'] for wc in words_cards], 
                                 box_color=(255, 255, 255), text_color=(255, 153, 51))

    # 返回图片和fishes
    return image, fishes
    

def main():
    INPUT_PATH = 'fish_grid.jpg'
    OUTPUT_IMAGE_PATH = 'main_result.png'

    image, fishes = extract_fishes(image_path=os.path.join(current_dir, INPUT_PATH))
    save_image_to_file(image, os.path.join(current_dir, OUTPUT_IMAGE_PATH))

if __name__ == "__main__":
    main()