from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QToolBar
from .grid_view import GridView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.grid = None
        self.grid_view = None
        self.init_ui()
        
    def init_ui(self):
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建工具栏
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 添加缩放按钮
        zoom_in_btn = QPushButton("+")
        zoom_out_btn = QPushButton("-")
        toolbar.addWidget(zoom_in_btn)
        toolbar.addWidget(zoom_out_btn)
        
        # 创建点阵视图
        self.grid_view = GridView()
        layout.addWidget(self.grid_view)
        
        # 设置窗口属性
        self.setWindowTitle("点阵编辑器")
        self.resize(800, 600)
        
    def load_grid(self, grid):
        """加载点阵数据"""
        self.grid = grid
        self.grid_view.set_grid(grid)