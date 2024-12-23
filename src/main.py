from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from core.grid import Grid
import sys

def main():
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 创建网格
    grid = Grid(318, 74)
    
    # 创建主窗口
    window = MainWindow(grid)
    window.show()
    
    # 运行应用程序事件循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 