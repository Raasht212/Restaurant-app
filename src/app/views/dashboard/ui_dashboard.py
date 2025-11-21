

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QSizePolicy, QSpacerItem, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)
import datetime

fecha_actual = datetime.datetime.now()

class Ui_Dashboard(object):
    def setupUi(self, Dashboard):
        if not Dashboard.objectName():
            Dashboard.setObjectName(u"Dashboard")
        Dashboard.resize(1253, 800)
        Dashboard.setStyleSheet(u"background-color: rgb(33, 33, 33);\n"
"color: rgb(255, 255, 255);\n"
"\n"
"")
        self.verticalLayout = QVBoxLayout(Dashboard)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(Dashboard)
        self.frame.setObjectName(u"frame")
        self.frame.setMaximumSize(QSize(16777215, 16777215))
        self.frame.setStyleSheet(u"QLabel {\n"
"	color: rgb(255, 255, 255);\n"
"	font: 600 10pt \"Segoe UI\";\n"
"}")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.horizontalSpacer = QSpacerItem(911, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.label_5 = QLabel(self.frame)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_2.addWidget(self.label_5)


        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(Dashboard)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setStyleSheet(u"background-color: transparent;\n"
"\n"
"QLabel {\n"
"	color: rgb(255, 255, 255);\n"
"	font: 600 10pt \"Segoe UI\";\n"
"}")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_2)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 1)
        self.frame_7 = QFrame(self.frame_2)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setStyleSheet(u"QFrame {\n"
"\n"
"	background-color: rgb(76, 0, 19);\n"
"border-radius: 10px;\n"
"\n"
"}")
        self.frame_7.setFrameShape(QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.frame_7)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_7 = QLabel(self.frame_7)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout_6.addWidget(self.label_7)

        self.label_11 = QLabel(self.frame_7)
        self.label_11.setObjectName(u"label_11")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(28)
        font.setBold(True)
        font.setItalic(False)
        self.label_11.setFont(font)
        self.label_11.setStyleSheet(u"font: 600 28pt \"Segoe UI\";")
        self.label_11.setAlignment(Qt.AlignCenter)

        self.verticalLayout_6.addWidget(self.label_11)

        self.verticalLayout_6.setStretch(0, 1)
        self.verticalLayout_6.setStretch(1, 10)

        self.horizontalLayout.addWidget(self.frame_7)

        self.frame_8 = QFrame(self.frame_2)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setStyleSheet(u"QFrame {\n"
"background-color: rgb(76, 0, 19);\n"
"border-radius: 10px;\n"
"\n"
"}")
        self.frame_8.setFrameShape(QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.frame_8)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label_12 = QLabel(self.frame_8)
        self.label_12.setObjectName(u"label_12")

        self.verticalLayout_7.addWidget(self.label_12)

        self.label_20 = QLabel(self.frame_8)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setFont(font)
        self.label_20.setStyleSheet(u"font: 600 28pt \"Segoe UI\";")
        self.label_20.setAlignment(Qt.AlignCenter)

        self.verticalLayout_7.addWidget(self.label_20)

        self.verticalLayout_7.setStretch(0, 1)
        self.verticalLayout_7.setStretch(1, 7)

        self.horizontalLayout.addWidget(self.frame_8)

        self.frame_9 = QFrame(self.frame_2)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setStyleSheet(u"QFrame {\n"
"background-color: rgb(76, 0, 19);\n"
"border-radius: 10px;\n"
"\n"
"}")
        self.frame_9.setFrameShape(QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.frame_9)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label_8 = QLabel(self.frame_9)
        self.label_8.setObjectName(u"label_8")

        self.verticalLayout_8.addWidget(self.label_8)

        self.label_13 = QLabel(self.frame_9)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setFont(font)
        self.label_13.setStyleSheet(u"font: 600 28pt \"Segoe UI\";")
        self.label_13.setAlignment(Qt.AlignCenter)

        self.verticalLayout_8.addWidget(self.label_13)

        self.label_14 = QLabel(self.frame_9)
        self.label_14.setObjectName(u"label_14")

        self.verticalLayout_8.addWidget(self.label_14)


        self.horizontalLayout.addWidget(self.frame_9)

        self.frame_10 = QFrame(self.frame_2)
        self.frame_10.setObjectName(u"frame_10")
        self.frame_10.setStyleSheet(u"QFrame {\n"
"background-color: rgb(76, 0, 19);\n"
"border-radius: 10px;\n"
"\n"
"}")
        self.frame_10.setFrameShape(QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QFrame.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.frame_10)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.label_15 = QLabel(self.frame_10)
        self.label_15.setObjectName(u"label_15")

        self.verticalLayout_9.addWidget(self.label_15)

        self.label_17 = QLabel(self.frame_10)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setFont(font)
        self.label_17.setStyleSheet(u"font: 600 28pt \"Segoe UI\";")
        self.label_17.setAlignment(Qt.AlignCenter)

        self.verticalLayout_9.addWidget(self.label_17)

        self.label_18 = QLabel(self.frame_10)
        self.label_18.setObjectName(u"label_18")

        self.verticalLayout_9.addWidget(self.label_18)


        self.horizontalLayout.addWidget(self.frame_10)


        self.verticalLayout.addWidget(self.frame_2)

        self.frame_3 = QFrame(Dashboard)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setStyleSheet(u"background-color: transparent;\n"
"\n"
"QLabel {\n"
"	color: rgb(255, 255, 255);\n"
"	font: 600 10pt \"Segoe UI\";\n"
"}")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setSpacing(15)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, -1)
        self.frame_4 = QFrame(self.frame_3)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setStyleSheet(u"background-color: transparent;")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_4)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_12 = QFrame(self.frame_4)
        self.frame_12.setObjectName(u"frame_12")
        self.frame_12.setStyleSheet(u"QFrame {\n"
"background-color: rgb(76, 0, 19);\n"
"border-radius: 10px;\n"
"\n"
"}")
        self.frame_12.setFrameShape(QFrame.StyledPanel)
        self.frame_12.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_12)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        #self.label_21 = QLabel(self.frame_12)
        #self.label_21.setObjectName(u"label_21")
        #self.label_21.setMaximumSize(QSize(16777215, 20))

        #self.verticalLayout_3.addWidget(self.label_21)

        self.frame_11 = QFrame(self.frame_12)
        self.frame_11.setObjectName(u"frame_11")
        self.frame_11.setFrameShape(QFrame.StyledPanel)
        self.frame_11.setFrameShadow(QFrame.Raised)

        self.verticalLayout_3.addWidget(self.frame_11)


        self.verticalLayout_4.addWidget(self.frame_12)

        self.frame_15 = QFrame(self.frame_4)
        self.frame_15.setObjectName(u"frame_15")
        self.frame_15.setStyleSheet(u"QFrame {\n"
"background-color: rgb(76, 0, 19);\n"
"border-radius: 10px;\n"
"\n"
"}")
        self.frame_15.setFrameShape(QFrame.StyledPanel)
        self.frame_15.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_15)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        #self.label_22 = QLabel(self.frame_15)
        #self.label_22.setObjectName(u"label_22")
        #self.label_22.setMaximumSize(QSize(16777215, 20))

        #self.verticalLayout_2.addWidget(self.label_22)

        self.frame_6 = QFrame(self.frame_15)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Raised)

        self.verticalLayout_2.addWidget(self.frame_6)


        self.verticalLayout_4.addWidget(self.frame_15)


        self.horizontalLayout_3.addWidget(self.frame_4)

        self.frame_5 = QFrame(self.frame_3)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setStyleSheet(u"background-color: rgb(76, 0, 19);\n"
"border-radius: 10px;\n"
"")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_5)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_23 = QLabel(self.frame_5)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setMaximumSize(QSize(16777215, 20))

        self.verticalLayout_5.addWidget(self.label_23)

        self.tableWidget = QTableWidget(self.frame_5)
        if (self.tableWidget.columnCount() < 4):
            self.tableWidget.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        if (self.tableWidget.rowCount() < 9):
            self.tableWidget.setRowCount(9)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(2, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(3, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(4, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(5, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(6, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(7, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(8, __qtablewidgetitem12)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setStyleSheet(u"color: rgb(0, 0, 0);\n"
"background-color: transparent;")

        self.verticalLayout_5.addWidget(self.tableWidget)


        self.horizontalLayout_3.addWidget(self.frame_5)

        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 1)

        self.verticalLayout.addWidget(self.frame_3)

        self.verticalLayout.setStretch(1, 2)
        self.verticalLayout.setStretch(2, 7)

        self.retranslateUi(Dashboard)

        QMetaObject.connectSlotsByName(Dashboard)
    # setupUi

    def retranslateUi(self, Dashboard):
        Dashboard.setWindowTitle(QCoreApplication.translate("Dashboard", u"Form", None))
        self.label.setText(QCoreApplication.translate("Dashboard", u"Hola Jose", None))
        self.label_5.setText(QCoreApplication.translate("Dashboard", fecha_actual.strftime("%d %B %Y"), None))
        self.label_7.setText(QCoreApplication.translate("Dashboard", u"Tasa del Dia", None))
        self.label_11.setText(QCoreApplication.translate("Dashboard", u"240 VEZ", None))
        self.label_12.setText(QCoreApplication.translate("Dashboard", u"Mesas Disponibles", None))
        self.label_20.setText(QCoreApplication.translate("Dashboard", u"20", None))
        self.label_8.setText(QCoreApplication.translate("Dashboard", u"Ordenes del dia", None))
        self.label_13.setText(QCoreApplication.translate("Dashboard", u"23", None))
        self.label_14.setText(QCoreApplication.translate("Dashboard", u"+15% Respecto a ayer", None))
        self.label_15.setText(QCoreApplication.translate("Dashboard", u"Ventas del dia", None))
        self.label_17.setText(QCoreApplication.translate("Dashboard", u"$8541", None))
        self.label_18.setText(QCoreApplication.translate("Dashboard", u"+30% Respecto a ayer", None))
        #self.label_21.setText(QCoreApplication.translate("Dashboard", u"Grafica Ventas Mensuales", None))
        #self.label_22.setText(QCoreApplication.translate("Dashboard", u"Grafica Ventas por Categoria", None))
        self.label_23.setText(QCoreApplication.translate("Dashboard", u"Lista Ordenes Abiertas", None))
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Dashboard", u"Cliente", None));
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Dashboard", u"Mesa", None));
        ___qtablewidgetitem2 = self.tableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Dashboard", u"Monto", None));
        ___qtablewidgetitem3 = self.tableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Dashboard", u"Ver Orden", None));
        ___qtablewidgetitem4 = self.tableWidget.verticalHeaderItem(0)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Dashboard", u"1", None));
        ___qtablewidgetitem5 = self.tableWidget.verticalHeaderItem(1)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("Dashboard", u"2", None));
        ___qtablewidgetitem6 = self.tableWidget.verticalHeaderItem(2)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("Dashboard", u"3", None));
        ___qtablewidgetitem7 = self.tableWidget.verticalHeaderItem(3)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("Dashboard", u"4", None));
        ___qtablewidgetitem8 = self.tableWidget.verticalHeaderItem(4)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("Dashboard", u"5", None));
        ___qtablewidgetitem9 = self.tableWidget.verticalHeaderItem(5)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("Dashboard", u"6", None));
        ___qtablewidgetitem10 = self.tableWidget.verticalHeaderItem(6)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("Dashboard", u"7", None));
        ___qtablewidgetitem11 = self.tableWidget.verticalHeaderItem(7)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("Dashboard", u"8", None));
        ___qtablewidgetitem12 = self.tableWidget.verticalHeaderItem(8)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("Dashboard", u"9", None));
    # retranslateUi

