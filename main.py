"""
App execute from here.
---
"""
import sys

# import os

from PyQt5.QtWidgets import QApplication

from UI import MainWindowControl

# if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
#     os.chdir(sys._MEIPASS)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwin = MainWindowControl()
    mainwin.initCharts()
    sys.exit(app.exec_())
