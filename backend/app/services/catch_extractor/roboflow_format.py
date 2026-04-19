from typing import Dict

def convert_yolo_to_standard(input: Dict) -> Dict:
    """
    将YOLO检测结果转换为标准API格式
    
    参数:
        input: roboflow返回的json字符串反序列化得到的字典
    """
    try:
        # 读取YOLO检测结果
        yolo_result = input
        
        # 获取预测结果
        predictions = yolo_result['outputs'][0]['predictions']['predictions']
        # 获取原始图像信息
        original_width = yolo_result['outputs'][0]['predictions']['image']['width']
        original_height = yolo_result['outputs'][0]['predictions']['image']['height']
        
        # 转换为标准格式
        standard_format = {
            "result": [],
            "result_num": 0,
        }
        
        for idx, pred in enumerate(predictions):
            try:
                # 获取YOLO预测的边界框信息
                x_center = pred['x']
                y_center = pred['y']
                width = pred['width']
                height = pred['height']
                confidence = pred['confidence']
                class_name = pred['class']
                
                # 计算左上角和右下角坐标
                left = int(x_center - width/2)
                top = int(y_center - height/2)
                right = int(x_center + width/2)
                bottom = int(y_center + height/2)
                
                # 确保坐标在图像范围内
                left = max(0, left)
                top = max(0, top)
                right = min(original_width, right)
                bottom = min(original_height, bottom)
                
                # 计算实际宽度和高度
                actual_width = right - left
                actual_height = bottom - top
                
                # 生成信息文本
                confidence_percent = f"{confidence * 100:.0f}%"
                info_text = f"{class_name}-{confidence_percent}"
                
                # 创建标准格式的单个结果
                result_item = {
                    "info": info_text,
                    "location": {
                        "top": top,
                        "left": left,
                        "width": actual_width,
                        "height": actual_height
                    }
                }
                
                standard_format["result"].append(result_item)

            except Exception as e:
                print(f"处理预测 {idx} 时出错: {e}")
                continue
        
        # 更新结果数量
        standard_format["result_num"] = len(standard_format["result"])

        return standard_format
    
    except Exception as e:
        print(f"转换过程中发生错误: {e}")
        return False