class Region:
    def __init__(self, name: str, region_type: str):
        """
        初始化分割区域
        region_type: 'rectangle' 或 'polygon'
        """
        self.name = name
        self.type = region_type
        self.points = []  # 多边形顶点列表
        self.color = None  # 半透明填充颜色
        
    def add_point(self, row: int, col: int):
        """添加顶点"""
        self.points.append((row, col))
        
    def contains_point(self, row: int, col: int) -> bool:
        """判断点是否在区域内"""
        # 根据region_type实现不同的判断逻辑
        pass 