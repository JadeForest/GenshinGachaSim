"""
App execute from here.
---
"""
import sys
from PyQt5.QtWidgets import QApplication
from UI import MainWindowControl


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwin = MainWindowControl()
    mainwin.initCharts()
    sys.exit(app.exec_())
