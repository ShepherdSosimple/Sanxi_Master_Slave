
import sys
from SanxiUI_function import SanxiWindow
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_show = SanxiWindow()
    my_show.show()
    sys.exit(app.exec_())
