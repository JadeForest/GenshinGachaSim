"""
UI Logic controls
---
"""
from collections import Counter

from PyQt5 import uic
from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView
from PyQt5.QtWidgets import (QDialog, QHeaderView, QMessageBox,
                             QTableWidgetItem, QAbstractItemView)

from core import *
from data import *
from tools import *
from UI import *
from consts import *


class MainWindowControl:
    pullerClasses = (CharacterBannerPuller, WeaponBannerPuller, StandardBannerPuller)
    bannerClasses = (CharacterBanner, WeaponBanner, StandardBanner)

    def __init__(self) -> None:
        # load ui
        self.ui = self.initWindow()
        # init records
        self.outputModes = [0,0,0]
        self.star5xbdwaileNums = [0,0] # xiao_bao_di_wai_le
        self.star5xbdNums = [0,0]
        # connect signals & slots
        self.initConnects()
        # show ui
        self.ui.show()
        # init pullers
        self.pullers = [puller() for puller in self.pullerClasses]
        # set current tab
        self.changeTab(0)
        # init banners
        for i,_ in enumerate(self.pullers):
            self.setBanner(i)
        # set custom config
        self.custom_conf = (False, 0.6) # in percentage

    def initWindow(self):
        ui = uic.loadUi(r'ui\mainwindow.ui')
    
        poolTables = [ui.poolTable1, ui.poolTable2]
        for table in poolTables:
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table.verticalHeader().hide()
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.horizontalHeader().hide()
        outputTables = [ui.outputTable1, ui.outputTable2, ui.outputTable3]
        headers = [
            ['总抽数','物品','类型','星级','四星抽数','四星大保底','五星抽数','五星大保底'],
            ['总抽数','物品','类型','星级','四星抽数','四星大保底','五星抽数','五星大保底','定轨值'],
            ['总抽数','物品','类型','星级','四星抽数','五星抽数']
        ]
        colnums = [8,9,6]
        for i,table in enumerate(outputTables):
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)     
            table.verticalHeader().hide()
            table.setColumnCount(colnums[i])
            table.setHorizontalHeaderLabels(headers[i])
            table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
            table.hide()

        return ui

    def initConnects(self):
        # connect tab btns
        switchOutputBtns = [self.ui.switchOutputBtn1,self.ui.switchOutputBtn2,self.ui.switchOutputBtn3]
        for btn in switchOutputBtns:
            btn.clicked.connect(self.switchOutput)
        resetPullerBtns = [self.ui.resetPullerBtn1, self.ui.resetPullerBtn2, self.ui.resetPullerBtn3]
        for btn in resetPullerBtns:
            btn.clicked.connect(self.resetPuller)
        self.ui.editPoolBtn1.clicked.connect(lambda: self.chooseDialog(0))
        self.ui.editPoolBtn2.clicked.connect(lambda: self.chooseDialog(1))
        self.ui.saveBtn1.clicked.connect(lambda: self.saveConf(0))
        self.ui.saveBtn2.clicked.connect(lambda: self.saveConf(1))
        self.ui.pathBtn.clicked.connect(self.setWpPath)
        # connect universal btns
        self.ui.onePullBtn.clicked.connect(lambda: self.doMultiplePulls(1))
        self.ui.tenPullBtn.clicked.connect(lambda: self.doMultiplePulls(10))
        self.ui.customPullsBtn.clicked.connect(lambda: self.doMultiplePulls(int(self.ui.customPullsSpinbox.text())))
        self.ui.aboutBtn.clicked.connect(self.about)
        self.ui.advBtn.clicked.connect(self.advance)
        # connect tabs
        self.ui.tabs.currentChanged.connect(self.changeTab)

    def initCharts(self):
        for chart in self.ui.centralwidget.findChildren(QWebEngineView):
            chart.load(QUrl('file:///web/chart.html'))
        web_sets = QWebEngineSettings.globalSettings()
        web_sets.setAttribute(QWebEngineSettings.JavascriptEnabled, True)

    def switchOutput(self, index):
        self.outputModes[index] += 1
        self.outputModes[index] %= 2
        if self.outputModes[index]:
            self.outputTable.show()
            self.summaryList.hide()
            self.chart.hide()
            self.switchOutputBtn.setText('显示简略信息')
            return
        else:
            self.outputTable.hide()
            self.summaryList.show()
            self.chart.show()
            self.switchOutputBtn.setText('显示详细信息')
            return

    def setBanner(self, i, rateups=None, *args, **kwargs):
        if i == 2:
            self.pullers[i].set_banner(self.bannerClasses[i]())
            return
        if not rateups:
            rateups = SavedPool(i).get()
        banner = self.bannerClasses[i](rateups)
        if i == 1 and kwargs:
            banner.set_path(kwargs['path_name'])
        self.pullers[i].set_banner(banner)
        rateuplist = rateups[5]+rateups[4]
        for index,item in enumerate(rateuplist):
            poolTables = [self.ui.poolTable1, self.ui.poolTable2]
            poolTables[i].setItem(index,1,QTableWidgetItem(item[0]))
        if i == 1:
            self.ui.pathBox.clear()
            self.ui.pathBox.addItems([UNPATHED]+DataList.flatData(rateups[5]))

    def saveConf(self,i):
        SavedPool(i).save(self.puller.get_banner_rateups())
        QMessageBox.information(self.ui, '提示', '已保存该卡池信息。')

    def setWpPath(self, name):
        name = self.ui.pathBox.currentText()
        self.puller.reset_banner_path()
        rateups = self.puller.get_banner_rateups()
        if name != UNPATHED:
            self.setBanner(1, rateups, path_name=name)
            addRows([['当前定轨：',name]],self.poolTable)
        else:
            self.setBanner(1, rateups)
            self.poolTable.setRowCount(7)
        self.ui.pathBox.setCurrentText(name)
        self.ui.pathValue.setText('0/2')

    def changeTab(self, index):
        self.CURRTAB = index
        outputTables = [self.ui.outputTable1, self.ui.outputTable2, self.ui.outputTable3]
        self.outputTable = outputTables[index]

        switchOutputBtns = [self.ui.switchOutputBtn1,self.ui.switchOutputBtn2,self.ui.switchOutputBtn3]
        self.switchOutputBtn = switchOutputBtns[index]

        resetPullerBtns = [self.ui.resetPullerBtn1, self.ui.resetPullerBtn2, self.ui.resetPullerBtn3]
        self.resetPullerBtn = resetPullerBtns[index]

        charts = [self.ui.chart1, self.ui.chart2, self.ui.chart3]
        self.chart = charts[index]

        summaryLists = [self.ui.summaryList1, self.ui.summaryList2, self.ui.summaryList3]
        self.summaryList = summaryLists[index]

        pullNums = [self.ui.pullNum1, self.ui.pullNum2, self.ui.pullNum3]
        self.pullNum = pullNums[index]

        self.puller = self.pullers[index]
        if index == 0:
            self.poolTable = self.ui.poolTable1
            self.editPoolBtn = self.ui.editPoolBtn1
            return
        if index == 1:
            self.poolTable = self.ui.poolTable2
            self.editPoolBtn = self.ui.editPoolBtn2
    
    def resetPuller(self):
        i = self.CURRTAB
        msg = QMessageBox.question(self.ui,'提示','会清空该祈愿所有记录，确认重置？',QMessageBox.Ok|QMessageBox.Cancel,QMessageBox.Cancel)
        if msg == QMessageBox.Cancel:
            return
        rateups = self.puller.get_banner_rateups() if i!=2 else None
        self.pullers[i] = self.pullerClasses[i]()
        self.puller = self.pullers[i]
        self.setBanner(i, rateups)
        if i != 2:
            self.star5xbdNums[i] = 0
            self.star5xbdwaileNums[i] = 0
        self.outputTable.clearContents()
        self.outputTable.setRowCount(0)
        self.summaryList.clear()
        self.pullNum.display(0)
        self.chart.load(QUrl('file:///web/chart.html'))
        if self.CURRTAB == 1:
            self.setWpPath(UNPATHED)

    def doMultiplePulls(self, count):
        table_rows = []
        table_colors = []
        list_rows = []
        for info, item in self.puller.multiple_pull(count=count):
            row = [str(info[0]), item.name, item.type, item.rank_display, *[str(e) for e in info[1:]]]
            table_rows.append(row)
            color = None
            if item.rank != 3:
                star5count = info[2] if self.CURRTAB==2 else info[3]
                waile = self.isNotBid(item.rank)
                waiMark = '\t(歪)' if waile else ''
                if item.rank == 4:
                    cntMark = ''
                    color = VIOLET
                else:
                    cntMark = f'[{star5count}]'
                    color = GOLD
                    if self.CURRTAB!=2 and (info[4]==0 and info[-1]<2): #xiao bao di
                        if waile:
                            self.star5xbdwaileNums[self.CURRTAB] += 1
                        self.star5xbdNums[self.CURRTAB] += 1
                list_rows.append('第{0}抽:\t{1.name:<20}\t{2}'.format(info[0],item,cntMark)+waiMark)
            table_colors.append(color)
        addRows(table_rows, self.outputTable, colors=table_colors)
        addItems(list_rows, self.summaryList)
        self.pullNum.display(self.puller.counts[0]-1)
        self.statsUpdate()
        self.outputTable.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        if self.CURRTAB == 1:
            self.ui.pathValue.setText('{}/2'.format(self.puller.info()[-1]))

    def isNotBid(self, item_rank:int) -> bool:
        if self.CURRTAB == 2:
            return False
        info = self.puller.info()
        if item_rank == 4:
            return info[2]>0
        return info[4]>0

    def statsUpdate(self):
        ctr = Counter(readCols([2,3], self.outputTable))
        data = [ctr[WP+THREESTAR], ctr[(CH+FOURSTAR)], ctr[(WP+FOURSTAR)], 
                ctr[(CH+FIVESTAR)], ctr[(WP+FIVESTAR)]]
        self.chart.page().runJavaScript('setData([{},{},{},{},{}]);'.format(*data))

        star5countCol = 5 if self.CURRTAB==2 else 6
        star5count_lt = list(map(int,filterCol(3,star5countCol,FIVESTAR,self.outputTable)))
        star5cnt = len(star5count_lt)
        star5exp = round(sum(star5count_lt)/max(star5cnt,1),2)
        self.chart.page().runJavaScript('setExp({});'.format(star5exp))

        if self.CURRTAB != 2:
            ftftrate = round((1 - self.star5xbdwaileNums[self.CURRTAB]/max(self.star5xbdNums[self.CURRTAB],1))*100, 2)
            self.chart.page().runJavaScript('setFtFt({});'.format(ftftrate))

    def chooseDialog(self, type):
        if type == 0:
            self.dialog = ChDialogControl(self.puller.get_banner_rateups())
        elif type == 1:
            self.dialog = WpDialogControl(self.puller.get_banner_rateups())
        self.dialog.sig.connect(self.setBanner)
        self.dialog.ui.exec_()

    def about(self):
        msg = '原神抽卡模拟器\nGenshin GachaSim\nv{}\nGithub https://github.com/JadeForest/GenshinGachaSim'.format(VERSION)
        QMessageBox.information(None, '关于', msg)

    def advance(self):
        settingWin = AdvancedSettingControl(self.custom_conf)
        settingWin.sig.connect(self.setCustom)
        settingWin.ui.exec_()

    def setCustom(self, set_custom: bool, custom_rate):
        self.custom_conf = (set_custom, custom_rate)
        if set_custom:
            UPStar5ItemCustom.set_custom_prob(custom_rate*0.01)
            Star5ItemCustom.set_custom_prob(custom_rate*0.01)
            custom_items = (UPStar5ItemCustom, UPStar5ItemCustom, Star5ItemCustom)
            for i,puller in enumerate(self.pullers):
                puller.items[5] = custom_items[i]
        else:
            default_items = (UPStar5Item, UPStar5Weapon, Star5Item)
            for i,puller in enumerate(self.pullers):
                puller.items[5] = default_items[i]

        
class DialogControl(QDialog):
    uipath: str = None
    data: DataList = None
    sig: pyqtSignal = pyqtSignal(int,dict)
    seg: int = 0

    def __init__(self, curr_lists=None) -> None:
        super().__init__()
        self.ui = uic.loadUi(self.uipath)
        self.initUI(curr_lists)

    def initUI(self, curr_lists=None):
        self.ui.buttonBox.accepted.connect(self.accept)
        
        for i,box in enumerate(self.boxes[:self.seg]):
            box.addItems(self.data.names[5])
            box.setCurrentText(curr_lists[5][i][0])

        for i,box in enumerate(self.boxes[self.seg:]):
            box.addItems(self.data.names[4])
            box.setCurrentText(curr_lists[4][i][0])

    def accept(self):
        ret = {
            5:[self.data.data[5][box.currentIndex()] for box in self.boxes[:self.seg]],
            4:[self.data.data[4][box.currentIndex()] for box in self.boxes[self.seg:]]
        }
        self.sig.emit(self.type,ret)
        self.ui.close()

    @property
    def boxes(self):
        pass


class ChDialogControl(DialogControl):
    uipath = r'ui\dialog1.ui'
    data = DataList(C5S, C5L, C4)
    seg = 1
    type = 0
       
    @property    
    def boxes(self):
        return (self.ui.box5,
                self.ui.box41, self.ui.box42, self.ui.box43)


class WpDialogControl(DialogControl):
    uipath = r'ui\dialog2.ui'
    seg = 2
    type = 1
    data = DataList(W5S, W5L, W4S, W4L)
   
    @property
    def boxes(self):
        return (self.ui.box51, self.ui.box52,
                self.ui.box41, self.ui.box42, self.ui.box43, self.ui.box44, self.ui.box45)
    

class AdvancedSettingControl(QDialog):
    sig: pyqtSignal = pyqtSignal(bool,float)

    def __init__(self, config: tuple) -> None:
        super().__init__()
        self.ui = uic.loadUi(r'ui\advanced.ui')
        self.initUI(*config)

    def initUI(self, set_custom: bool, custom_rate):
        self.ui.buttonBox.accepted.connect(self.accept)

        if set_custom:
            self.ui.checkBox.setChecked(True)
            self.ui.spinBox.setValue(custom_rate)

    def accept(self):
        set_custom = self.ui.checkBox.isChecked()
        custom_rate = self.ui.spinBox.value()
        self.sig.emit(set_custom, custom_rate)
        self.ui.close()