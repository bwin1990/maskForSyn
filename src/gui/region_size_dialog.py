from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QSpinBox, QPushButton)

class RegionSizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置分割区域大小")
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 边长输入
        size_layout = QHBoxLayout()
        size_label = QLabel("边长:")
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(1, 100)  # 设置合理的范围
        self.size_spinbox.setValue(10)  # 默认边长
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_spinbox)
        
        # 确定取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # 添加到主布局
        layout.addLayout(size_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
    
    def get_size(self):
        """获取设置的边长"""
        return self.size_spinbox.value() 