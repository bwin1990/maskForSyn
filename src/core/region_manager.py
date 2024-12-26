from typing import Dict
from .region import Region
from PyQt6.QtGui import QColor
from PyQt6.QtCore import pyqtSignal, QObject

class RegionManager(QObject):
    """区域管理器"""
    # 添加信号
    region_added = pyqtSignal(str)  # 发送新添加的区域名称
    
    def __init__(self):
        super().__init__()  # 调用父类初始化
        self.regions: Dict[str, Region] = {}
        self.next_name = 'a'  # 下一个可用的区域名称
        self.used_names = set()  # 添加已使用名称的集合
        
    def create_region(self, size: int) -> Region:
        """创建新区域"""
        # 检查是否还有可用名称
        if len(self.regions) >= 26:
            raise ValueError("已达到最大区域数量限制(26个)")
            
        # 寻找下一个可用名称
        while self.next_name in self.used_names:  # 使用used_names而不是regions
            self.next_name = chr(ord(self.next_name) + 1)
            if self.next_name > 'z':
                self.next_name = 'a'
        
        # 创建新区域
        region = Region(self.next_name, size)
        
        # 设置区域颜色
        color = QColor()
        color.setHsv(
            (ord(self.next_name) - ord('a')) * 30 % 360,  # 色相
            100,  # 饱和度
            200   # 明度
        )
        color.setAlpha(100)  # 设置透明度
        region.color = color
        
        # 保存区域和名称
        self.regions[self.next_name] = region
        self.used_names.add(self.next_name)  # 添加到已使用名称集合
        
        # 发送信号
        self.region_added.emit(self.next_name)
        
        # 更新下一个可用名称
        self.next_name = chr(ord(self.next_name) + 1)
        if self.next_name > 'z':
            self.next_name = 'a'
            
        return region
    
    def remove_region(self, name: str):
        """删除区域"""
        if name in self.regions:
            del self.regions[name]
            self.used_names.remove(name)  # 从已使用名称集合中移除 