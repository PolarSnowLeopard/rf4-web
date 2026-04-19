import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
import base64
import urllib.parse
import re

class BoundingBox:
    """
    表示图像上的方框的工具类
    支持两种坐标表示法：
    1. 中心点坐标 + 宽高 (YOLO格式): x_center, y_center, width, height
    2. 左上角坐标 + 宽高 (百度OCR格式): left, top, width, height
    """
    
    def __init__(self, x=0, y=0, width=0, height=0, is_center_format=True, word=""):
        """
        初始化方框对象
        
        参数:
            x: x坐标(中心点x或左上角x即left)
            y: y坐标(中心点y或左上角y即top)
            width: 方框宽度
            height: 方框高度
            is_center_format: 是否为中心点格式
            word: 方框内的文字内容
        """
        self.width = width
        self.height = height
        self._word = word  # 直接设置内部变量
        
        if is_center_format:
            # 如果输入是中心点格式，存储中心点并计算左上角
            self.x_center = x
            self.y_center = y
            self.left = x - width / 2
            self.top = y - height / 2
        else:
            # 如果输入是左上角格式，存储左上角并计算中心点
            self.left = x
            self.top = y
            self.x_center = x + width / 2
            self.y_center = y + height / 2
        
        # 计算右下角坐标
        self.right = self.left + width
        self.bottom = self.top + height
    
    @classmethod
    def from_yolo_format(cls, x_center, y_center, width, height, word=""):
        """
        从YOLO格式(中心点+宽高)创建方框对象
        
        参数:
            x_center: 中心点x坐标
            y_center: 中心点y坐标
            width: 宽度
            height: 高度
            word: 方框内的文字内容
        
        返回:
            BoundingBox对象
        """
        return cls(x_center, y_center, width, height, is_center_format=True, word=word)
    
    @classmethod
    def from_baidu_format(cls, left, top, width, height, word=""):
        """
        从百度OCR格式(左上角+宽高)创建方框对象
        
        参数:
            left: 左上角x坐标
            top: 左上角y坐标
            width: 宽度
            height: 高度
            word: 方框内的文字内容
        
        返回:
            BoundingBox对象
        """
        return cls(left, top, width, height, is_center_format=False, word=word)
    
    def get_yolo_format(self):
        """
        获取YOLO格式的坐标表示(中心点+宽高)
        
        返回:
            dict: 包含x, y, width, height的字典
        """
        return {
            "x": self.x_center,
            "y": self.y_center,
            "width": self.width,
            "height": self.height
        }
    
    def get_baidu_format(self):
        """
        获取百度OCR格式的坐标表示(左上角+宽高)
        
        返回:
            dict: 包含left, top, width, height的字典
        """
        return {
            "left": int(self.left),
            "top": int(self.top),
            "width": int(self.width),
            "height": int(self.height)
        }
    
    def get_corners(self):
        """
        获取方框的四个角点坐标
        
        返回:
            tuple: (左上角(x,y), 右上角(x,y), 右下角(x,y), 左下角(x,y))
        """
        return (
            (self.left, self.top),                  # 左上角
            (self.right, self.top),                 # 右上角
            (self.right, self.bottom),              # 右下角
            (self.left, self.bottom)                # 左下角
        )
    
    def is_overlapping(self, other: 'BoundingBox', error_margin: int=10):
        """
        判断本方框是否与另一个方框有重叠部分
        
        参数:
            other: 另一个BoundingBox对象
            error_margin: 误差范围（仅横向）
        
        返回:
            bool: 如果有重叠则返回True，否则返回False
        """
        # 如果一个方框在另一个方框的左边或右边，则不重叠（允许误差）
        if self.right < other.left - error_margin or self.left > other.right + error_margin:
            return False
        
        # 如果一个方框在另一个方框的上边或下边，则不重叠（不允许误差）
        if self.bottom < other.top or self.top > other.bottom:
            return False
        
        # 其他情况下，两个方框重叠
        return True
    
    def overlap_area(self, other):
        """
        计算与另一个方框的重叠面积
        
        参数:
            other: 另一个BoundingBox对象
        
        返回:
            float: 重叠面积，如果没有重叠则为0
        """
        if not self.is_overlapping(other):
            return 0
        
        # 计算重叠区域的宽和高
        overlap_width = min(self.right, other.right) - max(self.left, other.left)
        overlap_height = min(self.bottom, other.bottom) - max(self.top, other.top)
        
        # 计算重叠面积
        return overlap_width * overlap_height
    
    def iou(self, other):
        """
        计算与另一个方框的交并比(IoU: Intersection over Union)
        
        参数:
            other: 另一个BoundingBox对象
        
        返回:
            float: IoU值，范围[0, 1]
        """
        # 计算重叠面积
        overlap = self.overlap_area(other)
        if overlap == 0:
            return 0
        
        # 计算两个方框的面积
        area_self = self.width * self.height
        area_other = other.width * other.height
        
        # 计算并集面积
        area_union = area_self + area_other - overlap
        
        # 计算IoU
        return overlap / area_union
    
    @property
    def word(self):
        """获取方框内的文字内容"""
        return self._word
    
    @word.setter
    def word(self, value):
        """设置方框内的文字内容"""
        self._word = value
    
    def __str__(self):
        """字符串表示"""
        return (f"BoundingBox(center=({self.x_center:.1f}, {self.y_center:.1f}), "
                f"left-top=({self.left:.1f}, {self.top:.1f}), "
                f"width={self.width:.1f}, height={self.height:.1f}, "
                f"word='{self.word}')")
    
    def __add__(self, other):
        """合并两个BoundingBox对象"""
        left = min(self.left, other.left)
        top = min(self.top, other.top)
        width = max(self.right, other.right) - left
        height = max(self.bottom, other.bottom) - top

        return BoundingBox(
            x=left,
            y=top,
            width=width, 
            height=height,
            is_center_format=False,
            word=self.word + other.word
        )
    

def load_image_from_url(url: str) -> Image.Image:
    """
    从URL加载图片
    
    参数:
        url: 图片的URL
    
    返回:
        PIL.Image.Image: 加载的图片对象
    """
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

def save_image_to_file(image: Image.Image, file_path: str):
    """
    保存图片到文件
    
    参数:
        image: 图片对象
        file_path: 保存路径
    """
    image.save(file_path)

def load_image_from_file(file_path: str) -> Image.Image:
    """
    从文件加载图片
    
    参数:
        file_path: 图片文件路径
    
    返回:
        PIL.Image.Image: 加载的图片对象
    """
    return Image.open(file_path)

def draw_bounding_boxes_on_image(image: Image.Image, 
                                 boxes: list[BoundingBox], 
                                 box_color=(255, 0, 0), 
                                 text_color=(255, 255, 255), 
                                 line_width=2, 
                                 save_path=None) -> Image.Image:
    """
    在图片上绘制多个方框及对应的文字
    
    参数:
        image: PIL.Image.Image对象
        boxes: BoundingBox对象列表
        box_color: 方框颜色，RGB元组，默认红色
        text_color: 文字颜色，RGB元组，默认白色
        line_width: 线条宽度，默认2
        save_path: 保存标注后图片的路径，为None时不保存
    
    返回:
        PIL.Image.Image: 标注后的图片对象
    """
    
    # 创建绘图对象
    draw = ImageDraw.Draw(image)
    
    # 设置字体
    try:
        # 尝试使用系统中支持中文的字体
        # Windows系统
        if os.name == 'nt':
            font = ImageFont.truetype("SimHei", 14)  # 黑体
        # macOS或Linux系统
        else:
            font = ImageFont.truetype("NotoSansCJK-Regular.ttc", 14)  # 思源黑体
    except IOError:
        try:
            # 备选字体
            font_paths = [
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",  # Linux
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # 文泉驿微米黑
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",    # 文泉驿正黑
                "/System/Library/Fonts/PingFang.ttc",  # macOS
                "C:/Windows/Fonts/simsun.ttc",  # Windows宋体
                "C:/Windows/Fonts/simhei.ttf",  # Windows黑体
                "C:/Windows/Fonts/msyh.ttc"     # Windows微软雅黑
            ]
            
            for path in font_paths:
                if os.path.exists(path):
                    font = ImageFont.truetype(path, 14)
                    break
            else:
                # 如果上述字体都不可用，尝试使用PIL内置的默认字体
                font = ImageFont.load_default()
                print("警告：未找到支持中文的字体，文字可能无法正确显示")
        except Exception as e:
            font = ImageFont.load_default()
            print(f"警告：加载字体时出错 ({e})，文字可能无法正确显示")
    
    # 在图片上标注每个框和文字
    for box in boxes:
        left = int(box.left)
        top = int(box.top)
        width = int(box.width)
        height = int(box.height)
        
        # 绘制矩形框
        draw.rectangle(
            [(left, top), (left + width, top + height)],
            outline=box_color,
            width=line_width
        )
        
        # 在框上方显示文字
        if box.word:
            draw.text((left, top - 15), box.word, fill=text_color, font=font)
    
    # 保存结果
    if save_path:
        image.save(save_path)
        print(f'已标注的图片已保存至: {save_path}')
    
    return image

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

def get_field_from_word(word: str) -> dict:
    """
    根据文字，识别字段
    :param word: 文字(ocr提取的)
    :return: 字段名，字段值
    """
    legal_fish_name = ["镜鲤", "鲤鲫鱼"]

    # 判断是否为时间百分比
    if "分" in word:
        word = word[:word.index("分")+1]
        return {"key": "time_percentage", "value": word}
    
    # 判断是否为重量
    if "克" in word or "公斤" in word:
        if "公斤" in word:
            word = word.replace("公斤", "")
        else:
            word = str(float(word.replace("克", "")) / 1000)
        return {"key": "weight", "value": word}
    
    # 判断是否为鱼类名称
    if word in legal_fish_name:
        return {"key": "fish_name", "value": word}
    
    # 判断是否为售价
    if re.match(r'^\d+(\.\d+)?$', word):
        return {"key": "price", "value": word}
    
    return {"key": "fish_name", "value": word}

# 示例用法
if __name__ == "__main__":
    # 创建方框示例
    box1 = BoundingBox(40, 10, 20, 20, False, "123")
    box2 = BoundingBox(10, 10, 20, 20, False, "456")
    
    # 输出方框信息
    print(f"方框1: {box1}")
    print(f"方框2: {box2}")
    
    box1 += box2
    print(f"合并后的方框: {box1}")


