# advanced_charts_plugin.py - Advanced Charts
# QGIS 4 + Qt6
# English / TS-ready

import os

from qgis.PyQt.QtCore import (
    QCoreApplication,
    QSettings,
    QTranslator,
)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import QgsApplication

from .chart_dialog import ChartDialog


class AdvancedChartsPlugin:
    """Advanced Charts QGIS plugin."""

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dlg = None
        self.translator = None

        self.plugin_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

    # ------------------------------------------------------------------
    # TRANSLATION
    # ------------------------------------------------------------------

    def _load_translation(self):
        """Load the plugin translation according to the QGIS locale."""

        # Remove a previously installed translator.
        if self.translator is not None:
            QCoreApplication.removeTranslator(
                self.translator
            )
            self.translator = None

        settings = QSettings()

        locale = settings.value(
            "locale/userLocale",
            "",
        )

        if not locale:
            locale = QgsApplication.locale()

        if not locale:
            locale = "en_US"

        locale = str(locale).replace(
            "-",
            "_",
        )

        # Examples:
        # it_IT -> it
        # en_US -> en
        # de_DE -> de
        language = locale.split("_")[0].lower()

        # Translation directory.
        i18n_dir = os.path.join(
            self.plugin_dir,
            "i18n",
        )

        translation_file = os.path.join(
            i18n_dir,
            f"qgis_advanced_charts_{language}.qm",
        )

        # Fallback to English.
        if not os.path.exists(translation_file):
            translation_file = os.path.join(
                i18n_dir,
                "qgis_advanced_charts_en.qm",
            )

        if not os.path.isfile(translation_file):
            return

        translator = QTranslator()

        if translator.load(translation_file):
            QCoreApplication.installTranslator(
                translator
            )

            self.translator = translator

    # ------------------------------------------------------------------
    # GUI
    # ------------------------------------------------------------------

    def initGui(self):
        """Initialize the plugin GUI."""

        # Load translation before creating GUI elements.
        self._load_translation()

        # Avoid creating the action more than once.
        if self.action is not None:
            return

        icon_path = os.path.join(
            self.plugin_dir,
            "icon.png",
        )

        if os.path.isfile(icon_path):
            icon = QIcon(icon_path)
        else:
            icon = QIcon()

        self.action = QAction(
            icon,
            self.tr("Advanced Charts"),
            self.iface.mainWindow(),
        )

        self.action.setObjectName(
            "AdvancedChartsAction"
        )

        self.action.triggered.connect(
            self.run
        )

        self.iface.addToolBarIcon(
            self.action
        )

        self.iface.addPluginToMenu(
            self.tr("Advanced Charts"),
            self.action,
        )

    # ------------------------------------------------------------------
    # RUN
    # ------------------------------------------------------------------

    def run(self):
        """Show the Advanced Charts dialog."""

        if self.dlg is None:
            self.dlg = ChartDialog(
                self.iface
            )

        if self.dlg is None:
            return

        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

    # ------------------------------------------------------------------
    # UNLOAD
    # ------------------------------------------------------------------

    def unload(self):
        """Unload the plugin."""

        if self.action is not None:
            try:
                self.iface.removeToolBarIcon(
                    self.action
                )

                self.iface.removePluginMenu(
                    self.tr("Advanced Charts"),
                    self.action,
                )
            finally:
                self.action.deleteLater()
                self.action = None

        if self.dlg is not None:
            try:
                self.dlg.close()
            finally:
                self.dlg.deleteLater()
                self.dlg = None

        if self.translator is not None:
            QCoreApplication.removeTranslator(
                self.translator
            )

            self.translator = None

    # ------------------------------------------------------------------
    # TRANSLATION HELPER
    # ------------------------------------------------------------------

    def tr(self, message):
        """Translate a plugin string."""

        return QCoreApplication.translate(
            "AdvancedChartsPlugin",
            message,
        )
