class Grid:
    def __init__(self, rows: int, cols: int):
        """初始化点阵"""
        self.rows = rows
        self.cols = cols
        self.points = np.zeros((rows, cols))  # 存储点阵数据
        
    def is_valid_point(self, row: int, col: int) -> bool:
        """检查点是否在有效范围内"""
        return 0 <= row < self.rows and 0 <= col < self.cols 