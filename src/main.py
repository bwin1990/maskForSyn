import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from core.grid import Grid

def main():
    app = QApplication(sys.argv)
    
    # 创建一个测试用的点阵（以23k芯片为例）
    grid = Grid(318, 74)
    
    # 创建主窗口并显示
    window = MainWindow()
    window.load_grid(grid)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 