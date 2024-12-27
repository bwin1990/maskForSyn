from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QScrollArea)
from PyQt6.QtCore import pyqtSignal, Qt

class RegionControlPanel(QWidget):
    """分割框控制面板"""
    region_selected = pyqtSignal(str)  # 发送选中的区域名称
    region_deleted = pyqtSignal(str)   # 发送要删除的区域名称
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)  # 减少边距
        
        # 添加标题
        title = QLabel("分割框控制")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 创建容器widget
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setContentsMargins(2, 2, 2, 2)  # 减少边距
        self.container_layout.setSpacing(2)  # 减少间距
        self.container.setLayout(self.container_layout)
        
        # 将容器放入滚动区域
        scroll.setWidget(self.container)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
        self.setFixedWidth(150)  # 固定宽度
        
        # 存储按钮字典
        self.region_buttons = {}
    
    def add_region(self, name: str):
        """添加新的区域按钮"""
        # 检查区域名称是否已存在,避免重复添加
        if name in self.region_buttons:
            return
            
        # 创建一个新的widget作为按钮组的容器
        button_widget = QWidget()
        # 创建水平布局来放置按钮
        layout = QHBoxLayout()
        # 设置布局的边距为0,使按钮紧凑排列
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建区域选择按钮,显示大写的区域名称
        select_btn = QPushButton(name.upper())
        # 设置按钮固定高度为30像素
        select_btn.setFixedHeight(30)
        # 连接按钮点击信号,发送区域选中信号
        select_btn.clicked.connect(lambda: self.region_selected.emit(name))
        
        # 创建删除按钮,使用×符号
        delete_btn = QPushButton("×")
        # 设置删除按钮为固定大小30x30像素
        delete_btn.setFixedSize(30, 30)
        # 连接删除按钮的点击信号到delete_region方法
        delete_btn.clicked.connect(lambda: self.delete_region(name))
        
        # 将两个按钮添加到水平布局中
        layout.addWidget(select_btn)
        layout.addWidget(delete_btn)
        # 设置按钮组容器的布局
        button_widget.setLayout(layout)
        
        # 将按钮组widget保存到字典中以便后续管理
        self.region_buttons[name] = button_widget
        
        # 将按钮组添加到主容器的布局中
        self.container_layout.addWidget(button_widget)
    
    def delete_region(self, name: str):
        """删除区域按钮"""
        # 检查要删除的区域是否存在
        if name in self.region_buttons:
            # 获取对应的按钮组件
            button_widget = self.region_buttons[name]
            # 从容器布局中移除按钮组
            self.container_layout.removeWidget(button_widget)
            # 调用deleteLater()延迟删除组件
            button_widget.deleteLater()
            # 从按钮字典中删除记录
            del self.region_buttons[name]
            # 发送区域删除信号
            self.region_deleted.emit(name)
    
    def clear(self):
        """清除所有按钮"""
        # 遍历所有按钮组件并删除
        for button_widget in self.region_buttons.values():
            button_widget.deleteLater()
        # 清空按钮字典
        self.region_buttons.clear() 
    
    def remove_region(self, name: str):
        """从控制面板中移除区域"""
        # 检查要删除的区域是否存在于按钮字典中
        if name in self.region_buttons:
            # 获取对应的按钮组件
            button_widget = self.region_buttons[name]
            # 从容器布局中移除按钮组
            self.container_layout.removeWidget(button_widget)
            # 删除按钮组件
            button_widget.deleteLater()
            # 从按钮字典中删除记录
            del self.region_buttons[name]