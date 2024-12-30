import numpy as np
from typing import Dict
from PyQt6.QtCore import QPointF

class Grid:
    def __init__(self, rows: int, cols: int):
        """初始化点阵"""
        self.rows = rows
        self.cols = cols
        self.points = np.zeros((rows, cols))  # 存储点阵数据
        
    def is_valid_point(self, row: int, col: int) -> bool:
        """检查点是否在有效范围内"""
        return 0 <= row < self.rows and 0 <= col < self.cols 
        
    def convert_row(self, row: int) -> int:
        """转换行索引，实现从下往上的递增顺序"""
        return self.rows - 1 - row
        
    def get_point(self, row: int, col: int) -> int:
        """获取点的值，使用转换后的行索引"""
        converted_row = self.convert_row(row)
        if self.is_valid_point(converted_row, col):
            return self.points[converted_row, col]
        return 0
        
    def set_point(self, row: int, col: int, value: int):
        """设置点的值，使用转换后的行索引"""
        converted_row = self.convert_row(row)
        if self.is_valid_point(converted_row, col):
            self.points[converted_row, col] = value 
            
    def export_mask(self, regions: Dict[str, 'Region'], filename: str = "mask.txt"):
        """导出mask文件
        每个网格点占一行，按照从左到右，从上到下的顺序输出
        如果某个点被region覆盖，输出region的名称
        如果没有被覆盖，输出"0"
        """
        with open(filename, 'w', encoding='utf-8') as f:
            for row in range(self.rows):
                for col in range(self.cols):
                    # 检查当前点是否被任何region覆盖
                    covered = False
                    for region in regions.values():
                        if region.is_placed and region.contains_point(QPointF(col, row)):
                            f.write(f"{region.name.upper()}\n")
                            covered = True
                            break
                    
                    if not covered:
                        f.write("0\n") 