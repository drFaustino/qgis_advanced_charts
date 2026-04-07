# advanced_charts_plugin.py

import os
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication
from .chart_dialog import ChartDialog
from qgis.PyQt.QtCore import QTranslator, QLocale


class AdvancedChartsPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dlg = None
        self.plugin_dir = os.path.dirname(__file__)

        # --- Load translations (.qm) ---
        locale = QLocale.system().name()  # es. "it_IT"
        locale_short = locale.split("_")[0]
        locale_path = os.path.join(self.plugin_dir, "i18n", f"qgis_advanced_charts_{locale_short}.qm")

        self.translator = QTranslator()

        if os.path.exists(locale_path):
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        self.action = QAction(
            QIcon(icon_path) if os.path.exists(icon_path) else QIcon(),
            self.tr("Advanced Charts"),
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)

        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.tr("Advanced Charts"), self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu(self.tr("Advanced Charts"), self.action)

    def run(self):
        if self.dlg is None:
            self.dlg = ChartDialog(self.iface)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

    def tr(self, message):
        return QCoreApplication.translate("AdvancedChartsPlugin", message)
