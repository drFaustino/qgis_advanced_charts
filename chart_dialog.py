# chart_dialog.py — Advanced Charts
# QGIS 4 + Qt6, Matplotlib backend, TS-ready (English)

import os
import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QVariant, QDate, QDateTime
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QMessageBox,
    QSizePolicy,
)

from qgis.core import QgsProject, QgsField


FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        "advanced_charts_dialog.ui"
    )
)


class ChartDialog(QDialog, FORM_CLASS):

    def __init__(self, iface):
        super().__init__()

        self.setupUi(self)

        self.iface = iface

        # -------------------------------------------------------------
        # WINDOW / PLOT AREA
        # -------------------------------------------------------------

        self.setMinimumSize(1100, 650)

        # Keep the plot panel usable.
        self.groupBoxPlot.setMinimumSize(600, 500)

        # Make the plot layout expandable.
        self.plotLayout.setContentsMargins(6, 6, 6, 6)
        self.plotLayout.setSpacing(0)

        # -------------------------------------------------------------
        # MATPLOTLIB CANVAS
        # -------------------------------------------------------------

        self.figure = plt.Figure(
            figsize=(7.0, 5.5),
            dpi=100
        )

        self.canvas = FigureCanvas(self.figure)

        self.canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        self.canvas.setMinimumSize(0, 0)

        self.plotLayout.addWidget(self.canvas, 1)

        # -------------------------------------------------------------
        # PROGRESS
        # -------------------------------------------------------------

        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)

        # -------------------------------------------------------------
        # UI
        # -------------------------------------------------------------

        self._init_tooltips()
        self._init_style_controls()
        self._init_defaults()

        # -------------------------------------------------------------
        # LAYERS
        # -------------------------------------------------------------

        self.populate_layers()

        # -------------------------------------------------------------
        # CONNECTIONS
        # -------------------------------------------------------------

        self.layerCombo.currentIndexChanged.connect(
            self.populate_fields
        )

        self.plotButton.clicked.connect(
            self.plot
        )

        self.saveButton.clicked.connect(
            self.save_plot
        )

        self.chartTypeCombo.currentIndexChanged.connect(
            self.on_chart_type_changed
        )

        self.separateSubplotsCheck.stateChanged.connect(
            self.on_subplot_option_changed
        )

        self.enableY2Check.stateChanged.connect(
            self.toggle_y2_title
        )

        self.clearButton.clicked.connect(
            self.clear_plot
        )

        self.closeButton.clicked.connect(
            self.close
        )

        self.selectedOnlyCheck.stateChanged.connect(
            self.populate_fields
        )

        # Reload button is optional in older UI files.
        if hasattr(self, "reloadButton"):
            self.reloadButton.clicked.connect(
                self.reload_layers
            )

        self.enableLinearRegressionCheck.setChecked(False)

        # -------------------------------------------------------------
        # INITIAL PLOT
        # -------------------------------------------------------------

        self.init_empty_plot()

    # =================================================================
    # UI INITIALIZATION
    # =================================================================

    def _init_tooltips(self):
        self.binSpin.setToolTip(
            self.tr(
                "Number of histogram bins.\n"
                "More bins = more detail.\n"
                "Fewer bins = simpler chart.\n"
                "Use high values only with large numeric datasets."
            )
        )

        self.selectedOnlyCheck.setToolTip(
            self.tr(
                "Use only selected features from the chosen layer."
            )
        )

        self.enableY2Check.setToolTip(
            self.tr(
                "Enable a secondary Y axis (Y2) for line or scatter charts."
            )
        )

        self.autoChartCheck.setToolTip(
            self.tr(
                "Automatically suggest a chart type based on X and Y field types."
            )
        )

        self.separateSubplotsCheck.setToolTip(
            self.tr(
                "Create a separate subplot for each Y field."
            )
        )

        if hasattr(self, "reloadButton"):
            self.reloadButton.setToolTip(
                self.tr(
                    "Reload layers and fields from the current QGIS project."
                )
            )

    # -----------------------------------------------------------------

    def _init_style_controls(self):

        markers = [
            "None",
            "o",
            "x",
            "s",
            "^",
            "v",
            "<",
            ">",
            "D",
            "d",
            "*",
            "+",
            "|",
            "_",
            "P",
            "X",
        ]

        line_styles = [
            "None",
            "-",
            "--",
            "-.",
            ":",
        ]

        self.markerCombo.clear()
        self.markerY2Combo.clear()

        self.markerCombo.addItems(markers)
        self.markerY2Combo.addItems(markers)

        self.lineStyleCombo.clear()
        self.lineStyleY2Combo.clear()

        self.lineStyleCombo.addItems(line_styles)
        self.lineStyleY2Combo.addItems(line_styles)

        self.colorWidgetY.setColor(
            QColor("#1f77b4")
        )

        self.colorWidgetY2.setColor(
            QColor("#d62728")
        )

        self.colorWidgetBg.setColor(
            QColor("#ffffff")
        )

        self.y2AxisTitleEdit.setEnabled(
            self.enableY2Check.isChecked()
        )

    # -----------------------------------------------------------------

    def _init_defaults(self):

        self.binSpin.setValue(10)

        self.gridCheck.setChecked(True)

        self.legendCheck.setChecked(True)

        self.selectedOnlyCheck.setChecked(False)

        self.separateSubplotsCheck.setChecked(False)

        self.autoChartCheck.setChecked(True)

        self.progressBar.setValue(0)

    # =================================================================
    # BUSY / PROGRESS
    # =================================================================

    def _set_busy(self, busy):

        if busy:

            self.progressBar.setValue(0)
            self.progressBar.setFormat(
                self.tr("Working... %p%")
            )

            QApplication.setOverrideCursor(
                Qt.CursorShape.WaitCursor
            )

            self.plotButton.setEnabled(False)
            self.saveButton.setEnabled(False)
            self.clearButton.setEnabled(False)

            if hasattr(self, "reloadButton"):
                self.reloadButton.setEnabled(False)

            QApplication.processEvents()

        else:

            self.progressBar.setValue(0)
            self.progressBar.setFormat("%p%")

            QApplication.restoreOverrideCursor()

            self.plotButton.setEnabled(True)
            self.saveButton.setEnabled(True)
            self.clearButton.setEnabled(True)

            if hasattr(self, "reloadButton"):
                self.reloadButton.setEnabled(True)

            QApplication.processEvents()

    # -----------------------------------------------------------------

    def _set_progress(self, value):

        value = max(
            0,
            min(
                100,
                int(value)
            )
        )

        self.progressBar.setValue(value)

        QApplication.processEvents()

    # =================================================================
    # EMPTY / CLEAR PLOT
    # =================================================================

    def init_empty_plot(self):

        # IMPORTANT:
        # Do NOT create a new FigureCanvas here.
        # The canvas must keep its original geometry.

        self.figure.clear()

        ax = self.figure.add_subplot(111)

        ax.set_facecolor("#ffffff")

        ax.grid(True)

        ax.set_title(
            self.tr("Chart"),
            fontweight="bold",
            pad=20
        )

        ax.set_xlabel(
            self.tr("X axis"),
            fontweight="bold",
            labelpad=15
        )

        ax.set_ylabel(
            self.tr("Y axis"),
            fontweight="bold",
            labelpad=15
        )

        self.figure.subplots_adjust(
            left=0.12,
            right=0.95,
            bottom=0.12,
            top=0.88
        )

        self.canvas.draw_idle()

    # -----------------------------------------------------------------

    def clear_plot(self):

        # IMPORTANT:
        # Keep the same Figure and the same FigureCanvas.
        # This prevents the plot widget from changing size.

        self.figure.clear()

        ax = self.figure.add_subplot(111)

        ax.set_facecolor("#ffffff")

        ax.grid(True)

        ax.set_title(
            self.tr("Chart"),
            fontweight="bold",
            pad=20
        )

        ax.set_xlabel(
            self.tr("X axis"),
            fontweight="bold",
            labelpad=15
        )

        ax.set_ylabel(
            self.tr("Y axis"),
            fontweight="bold",
            labelpad=15
        )

        self.figure.subplots_adjust(
            left=0.12,
            right=0.95,
            bottom=0.12,
            top=0.88
        )

        self.canvas.draw_idle()

        self.progressBar.setValue(0)

    # =================================================================
    # LAYERS
    # =================================================================

    def populate_layers(self):

        current_layer_id = None

        current_layer = self.layerCombo.currentData()

        if current_layer is not None:
            current_layer_id = current_layer.id()

        self.layerCombo.blockSignals(True)

        self.layerCombo.clear()

        for layer in QgsProject.instance().mapLayers().values():

            if not hasattr(layer, "fields"):
                continue

            self.layerCombo.addItem(
                layer.name(),
                layer
            )

        if current_layer_id:

            for index in range(self.layerCombo.count()):

                layer = self.layerCombo.itemData(index)

                if layer is not None and layer.id() == current_layer_id:

                    self.layerCombo.setCurrentIndex(index)
                    break

        self.layerCombo.blockSignals(False)

        self.populate_fields()

    # -----------------------------------------------------------------

    def reload_layers(self):

        self._set_busy(True)

        try:

            self.populate_layers()

            self.progressBar.setValue(100)

            QApplication.processEvents()

        except Exception as exc:

            QMessageBox.warning(
                self,
                self.tr("Advanced Charts"),
                self.tr(
                    "Unable to reload layers:\n{0}"
                ).format(str(exc))
            )

        finally:

            self._set_busy(False)

    # =================================================================
    # FIELDS
    # =================================================================

    def populate_fields(self):

        self.xFieldCombo.clear()

        self.yFieldsList.clear()

        self.y2FieldCombo.clear()

        layer = self.layerCombo.currentData()

        if layer is None:
            return

        if self.selectedOnlyCheck.isChecked():

            if layer.selectedFeatureCount() == 0:

                QMessageBox.warning(
                    self,
                    self.tr("Advanced Charts"),
                    self.tr(
                        "You enabled 'Use selected features only', "
                        "but no features are currently selected."
                    )
                )

                return

        for field in layer.fields():

            name = field.name()

            self.xFieldCombo.addItem(
                name
            )

            self.yFieldsList.addItem(
                name
            )

            self.y2FieldCombo.addItem(
                name
            )

    # =================================================================
    # DATA
    # =================================================================

    def get_features(self):

        layer = self.layerCombo.currentData()

        if layer is None:
            return []

        if self.selectedOnlyCheck.isChecked():
            return layer.selectedFeatures()

        return list(
            layer.getFeatures()
        )

    # -----------------------------------------------------------------

    def get_field_type(self, field: QgsField):

        if field.isNumeric():
            return "numeric"

        if field.type() in (
            QVariant.Date,
            QVariant.DateTime,
            QVariant.Time,
        ):
            return "date"

        if field.type() == QVariant.String:

            if "date" in field.name().lower():
                return "date_string"

            return "string"

        return "other"

    # -----------------------------------------------------------------

    def get_data(self, field_name):

        layer = self.layerCombo.currentData()

        if layer is None:
            return [], "other"

        field_index = layer.fields().indexOf(
            field_name
        )

        if field_index < 0:
            return [], "other"

        field = layer.fields()[field_index]

        ftype = self.get_field_type(
            field
        )

        values = []

        for feature in self.get_features():

            value = feature[field_name]

            if value is None:
                continue

            # ---------------------------------------------------------
            # QGIS DATE
            # ---------------------------------------------------------

            if isinstance(value, QDate):

                if value.isValid():
                    values.append(
                        value.toPyDate()
                    )

                continue

            # ---------------------------------------------------------
            # QGIS DATETIME
            # ---------------------------------------------------------

            if isinstance(value, QDateTime):

                if value.isValid():
                    values.append(
                        value.toPyDateTime()
                    )

                continue

            # ---------------------------------------------------------
            # DATE / DATETIME PYTHON
            # ---------------------------------------------------------

            if isinstance(
                value,
                datetime.datetime
            ):

                values.append(value)

                continue

            if isinstance(
                value,
                datetime.date
            ):

                values.append(value)

                continue

            # ---------------------------------------------------------
            # DATE STRING
            # ---------------------------------------------------------

            if ftype == "date_string":

                text = str(value).strip()
    
                parsed = False
    
                try:
                    values.append(
                        datetime.datetime.fromisoformat(
                            text
                        )
                    )
                    parsed = True
    
                except (
                    ValueError,
                    TypeError,
                ):
                    parsed = False
    
                if not parsed:
    
                    try:
                        values.append(
                            datetime.datetime.strptime(
                                text,
                                "%d/%m/%Y"
                            )
                        )
                        parsed = True
    
                    except ValueError:
                        parsed = False
    
                if not parsed:
    
                    try:
                        values.append(
                            datetime.datetime.strptime(
                                text,
                                "%d/%m/%Y %H:%M:%S"
                            )
                        )
                        parsed = True
    
                    except ValueError:
                        parsed = False
    
                if not parsed:
                    continue

            # ---------------------------------------------------------
            # NUMERIC
            # ---------------------------------------------------------

            elif ftype == "numeric":

                try:

                    values.append(
                        float(value)
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    continue

            # ---------------------------------------------------------
            # STRING
            # ---------------------------------------------------------

            elif ftype == "string":

                values.append(
                    str(value)
                )

            # ---------------------------------------------------------
            # OTHER
            # ---------------------------------------------------------

            else:

                values.append(value)

        # -------------------------------------------------------------
        # NORMALIZE DATE TYPES
        # -------------------------------------------------------------

        if ftype in (
            "date",
            "date_string",
        ):

            return values, "date"

        return values, ftype

    # -----------------------------------------------------------------

    def _convert_x(self, x_data, x_type):

        if x_type == "date":
            return mdates.date2num(x_data)

        return x_data

    # =================================================================
    # CHART TYPE
    # =================================================================

    def suggest_chart_type(
        self,
        x_type,
        y_types
    ):

        if (
            x_type == "string"
            and all(
                item == "numeric"
                for item in y_types
            )
        ):
            return "Bar"

        if (
            x_type == "date"
            and all(
                item == "numeric"
                for item in y_types
            )
        ):
            return "Line"

        if (
            x_type == "numeric"
            and all(
                item == "numeric"
                for item in y_types
            )
        ):
            return "Scatter"

        return "Histogram"

    # -----------------------------------------------------------------

    def on_chart_type_changed(self):

        chart_type = self.chartTypeCombo.currentText()

        self.binSpin.setEnabled(
            chart_type == "Histogram"
        )

        if self.separateSubplotsCheck.isChecked():

            if chart_type in (
                "Bar",
                "Pie",
                "Boxplot",
            ):

                QMessageBox.information(
                    self,
                    self.tr("Suggestion"),
                    self.tr(
                        "Separate subplot for each Y is not "
                        "recommended for Bar, Pie or Boxplot charts."
                    )
                )

    # -----------------------------------------------------------------

    def on_subplot_option_changed(self):

        if not self.separateSubplotsCheck.isChecked():
            return

        chart_type = self.chartTypeCombo.currentText()

        if chart_type in (
            "Bar",
            "Pie",
            "Boxplot",
        ):

            QMessageBox.information(
                self,
                self.tr("Suggestion"),
                self.tr(
                    "Separate subplots are not recommended for "
                    "this chart type."
                )
            )

    # -----------------------------------------------------------------

    def toggle_y2_title(self):

        self.y2AxisTitleEdit.setEnabled(
            self.enableY2Check.isChecked()
        )

    # =================================================================
    # MAIN PLOT
    # =================================================================

    def plot(self):

        self._set_busy(True)

        try:

            self._set_progress(5)

            layer = self.layerCombo.currentData()

            if layer is None:

                QMessageBox.warning(
                    self,
                    self.tr("Advanced Charts"),
                    self.tr("No layer selected.")
                )

                return

            x_field = self.xFieldCombo.currentText()

            if not x_field:

                QMessageBox.warning(
                    self,
                    self.tr("Advanced Charts"),
                    self.tr("Please select an X field.")
                )

                return

            selected_items = (
                self.yFieldsList.selectedItems()
            )

            if not selected_items:

                QMessageBox.warning(
                    self,
                    self.tr("Advanced Charts"),
                    self.tr(
                        "Please select at least one Y field."
                    )
                )

                return

            y_fields = [
                item.text()
                for item in selected_items
            ]

            self._set_progress(10)

            # ---------------------------------------------------------
            # X
            # ---------------------------------------------------------

            x_data, x_type = self.get_data(
                x_field
            )

            x_data = self._convert_x(
                x_data,
                x_type
            )

            if x_type == "date":

                x_data = np.asarray(
                    x_data,
                    dtype=float
                )

            else:

                x_data = np.asarray(
                    x_data,
                    dtype=object
                )

            if len(x_data) == 0:

                QMessageBox.warning(
                    self,
                    self.tr("Advanced Charts"),
                    self.tr(
                        "No valid data for X field: {0}"
                    ).format(x_field)
                )

                return

            self._set_progress(25)

            # ---------------------------------------------------------
            # Y
            # ---------------------------------------------------------

            y_data_list = []

            y_types = []

            for y_field in y_fields:

                data, field_type = self.get_data(
                    y_field
                )

                if not data:

                    QMessageBox.warning(
                        self,
                        self.tr("Advanced Charts"),
                        self.tr(
                            "No valid data for Y field: {0}"
                        ).format(y_field)
                    )

                    return

                y_data_list.append(
                    data
                )

                y_types.append(
                    field_type
                )

            # ---------------------------------------------------------
            # Y2
            # ---------------------------------------------------------

            use_y2 = self.enableY2Check.isChecked()

            y2_field = None
            y2_data = None
            y2_type = None

            if use_y2:

                y2_field = (
                    self.y2FieldCombo.currentText()
                )

                y2_data, y2_type = self.get_data(
                    y2_field
                )

                if not y2_data:

                    QMessageBox.warning(
                        self,
                        self.tr("Advanced Charts"),
                        self.tr(
                            "No valid data for Y2 field: {0}"
                        ).format(y2_field)
                    )

                    return

            self._set_progress(35)

            # ---------------------------------------------------------
            # AUTO CHART TYPE
            # ---------------------------------------------------------

            if self.autoChartCheck.isChecked():

                suggested = self.suggest_chart_type(
                    x_type,
                    y_types
                )

                index = self.chartTypeCombo.findText(
                    suggested
                )

                if index >= 0:
                    self.chartTypeCombo.setCurrentIndex(
                        index
                    )

            chart_type = (
                self.chartTypeCombo.currentText()
            )

            # ---------------------------------------------------------
            # DATE VALIDATION
            # ---------------------------------------------------------

            unsupported = (
                "Histogram",
                "Pie",
                "Boxplot",
                "Violin",
                "Radar",
                "Area",
                "Bar",
            )

            if (
                x_type == "date"
                and chart_type in unsupported
            ):

                QMessageBox.warning(
                    self,
                    self.tr("Advanced Charts"),
                    self.tr(
                        "The selected chart type does not support "
                        "date values on the X axis.\n\n"
                        "Supported chart types for date X fields are:\n"
                        "- Line\n"
                        "- Scatter\n"
                        "- Linear Regression\n"
                        "- Curve Fitting"
                    )
                )

                return

            # ---------------------------------------------------------
            # NUMERIC Y
            # ---------------------------------------------------------

            numeric_y_types = (
                "numeric",
                "date",
            )

            if chart_type not in (
                "Pie",
                "Histogram",
                "Boxplot",
                "Violin",
                "Radar",
            ):

                for index, data in enumerate(
                    y_data_list
                ):

                    if y_types[index] not in numeric_y_types:

                        QMessageBox.warning(
                            self,
                            self.tr("Advanced Charts"),
                            self.tr(
                                "Y field '{0}' must be numeric "
                                "for this chart type."
                            ).format(
                                y_fields[index]
                            )
                        )

                        return

            if use_y2 and y2_type != "numeric":

                QMessageBox.warning(
                    self,
                    self.tr("Advanced Charts"),
                    self.tr(
                        "Y2 field must be numeric."
                    )
                )

                return

            if use_y2:

                y2_data = np.asarray(
                    y2_data,
                    dtype=float
                )

            # ---------------------------------------------------------
            # HISTOGRAM
            # ---------------------------------------------------------

            if chart_type == "Histogram":

                self._suggest_bins(
                    y_data_list[0]
                )

            self._set_progress(45)

            # ---------------------------------------------------------
            # FIGURE
            # ---------------------------------------------------------

            # NEVER replace self.canvas.
            self.figure.clear()

            separate_subplots = (
                self.separateSubplotsCheck.isChecked()
            )

            n_series = len(
                y_fields
            )

            # ---------------------------------------------------------
            # STYLE
            # ---------------------------------------------------------

            base_color = (
                self.colorWidgetY.color().name()
            )

            bg_color = (
                self.colorWidgetBg.color().name()
            )

            marker = (
                self.markerCombo.currentText()
            )

            linestyle = (
                self.lineStyleCombo.currentText()
            )

            bins = self.binSpin.value()

            color_y2 = (
                self.colorWidgetY2.color().name()
            )

            marker_y2 = (
                self.markerY2Combo.currentText()
            )

            linestyle_y2 = (
                self.lineStyleY2Combo.currentText()
            )

            # ---------------------------------------------------------
            # COLOR CYCLE
            # ---------------------------------------------------------

            default_cycle = (
                plt.rcParams.get(
                    "axes.prop_cycle"
                )
            )

            if default_cycle is not None:

                cycle_colors = list(
                    default_cycle.by_key().get(
                        "color",
                        []
                    )
                )

            else:

                cycle_colors = []

            if not cycle_colors:
                cycle_colors = [
                    base_color
                ]

            cycle_colors[0] = base_color

            colors = cycle_colors

            # ---------------------------------------------------------
            # TITLES
            # ---------------------------------------------------------

            main_title = (
                self.mainTitleEdit.text().strip()
            )

            x_title = (
                self.xAxisTitleEdit.text().strip()
            )

            y_title = (
                self.yAxisTitleEdit.text().strip()
            )

            y2_title = (
                self.y2AxisTitleEdit.text().strip()
            )

            # ---------------------------------------------------------
            # AXES
            # ---------------------------------------------------------

            if (
                separate_subplots
                and n_series > 1
                and chart_type not in (
                    "Pie",
                    "Boxplot",
                    "Radar",
                )
            ):

                axes = []

                for index in range(n_series):

                    ax = self.figure.add_subplot(
                        n_series,
                        1,
                        index + 1
                    )

                    axes.append(ax)

            else:

                axes = [
                    self.figure.add_subplot(
                        111
                    )
                ]

            ax2 = None

            if use_y2:

                if chart_type in (
                    "Line",
                    "Scatter",
                    "Linear Regression",
                    "Curve Fitting",
                ):

                    ax2 = axes[0].twinx()

                else:

                    QMessageBox.warning(
                        self,
                        self.tr("Advanced Charts"),
                        self.tr(
                            "Y2 axis is only supported for "
                            "Line, Scatter, Linear Regression "
                            "and Curve Fitting."
                        )
                    )

                    return

            # ---------------------------------------------------------
            # DATE FORMAT
            # ---------------------------------------------------------

            if x_type == "date":

                for ax in axes:

                    ax.xaxis.set_major_formatter(
                        mdates.DateFormatter(
                            "%Y-%m-%d"
                        )
                    )

                    ax.xaxis.set_major_locator(
                        mdates.AutoDateLocator()
                    )

                if ax2 is not None:

                    ax2.xaxis.set_major_formatter(
                        mdates.DateFormatter(
                            "%Y-%m-%d"
                        )
                    )

                    ax2.xaxis.set_major_locator(
                        mdates.AutoDateLocator()
                    )

            self._set_progress(60)

            # ---------------------------------------------------------
            # DISPATCH
            # ---------------------------------------------------------

            self._plot_dispatch(
                fig=self.figure,
                axes=axes,
                ax2=ax2,
                chart_type=chart_type,
                x_data=x_data,
                x_field=x_field,
                y_fields=y_fields,
                y_data_list=y_data_list,
                y2_field=y2_field,
                y2_data=y2_data,
                separate_subplots=separate_subplots,
                colors=colors,
                color_y2=color_y2,
                bg_color=bg_color,
                marker=marker,
                linestyle=linestyle,
                marker_y2=marker_y2,
                linestyle_y2=linestyle_y2,
                bins=bins
            )

            self._set_progress(80)

            # ---------------------------------------------------------
            # AXIS TITLES
            # ---------------------------------------------------------

            axes[0].set_xlabel(
                x_title if x_title else x_field,
                fontweight="bold"
            )

            axes[0].set_ylabel(
                y_title
                if y_title
                else self.tr("Value"),
                fontweight="bold"
            )

            if use_y2 and ax2 is not None:

                ax2.set_ylabel(
                    y2_title
                    if y2_title
                    else (
                        y2_field
                        or self.tr("Y2")
                    ),
                    fontweight="bold"
                )

            # ---------------------------------------------------------
            # TITLE
            # ---------------------------------------------------------

            self.figure.suptitle(
                main_title
                if main_title
                else (
                    "{0} - {1}".format(
                        chart_type,
                        layer.name()
                    )
                ),
                fontweight="bold"
            )

            # ---------------------------------------------------------
            # LEGEND
            # ---------------------------------------------------------

            if (
                self.legendCheck.isChecked()
                and chart_type not in (
                    "Pie",
                    "Boxplot",
                    "Radar",
                )
            ):

                handles1, labels1 = (
                    axes[0].get_legend_handles_labels()
                )

                if use_y2 and ax2 is not None:

                    handles2, labels2 = (
                        ax2.get_legend_handles_labels()
                    )

                    if handles1 or handles2:

                        axes[0].legend(
                            handles1 + handles2,
                            labels1 + labels2
                        )

                elif handles1:

                    axes[0].legend(
                        handles1,
                        labels1
                    )

            # ---------------------------------------------------------
            # FINAL LAYOUT
            # ---------------------------------------------------------

            self.figure.subplots_adjust(
                left=0.12,
                right=0.94,
                bottom=0.12,
                top=0.88,
                hspace=0.35
            )

            self.canvas.draw_idle()

            self._set_progress(100)

            QApplication.processEvents()

        except Exception as exc:

            QMessageBox.critical(
                self,
                self.tr("Advanced Charts"),
                self.tr(
                    "Error while generating chart:\n\n{0}"
                ).format(str(exc))
            )

        finally:

            # Always return progress bar to zero.
            self._set_busy(False)

    # =================================================================
    # BINS
    # =================================================================

    def _suggest_bins(self, y_values):

        values = self._safe_float_list(
            y_values
        )

        n = len(values)

        if n < 2:
            return

        y_sorted = sorted(values)

        q1_index = int(
            0.25 * (n - 1)
        )

        q3_index = int(
            0.75 * (n - 1)
        )

        q1 = y_sorted[q1_index]

        q3 = y_sorted[q3_index]

        iqr = (
            q3 - q1
            if q3 > q1
            else 1
        )

        bin_width = (
            2
            * iqr
            * (n ** (-1 / 3))
        )

        value_range = (
            max(values)
            - min(values)
        )

        if bin_width <= 0:

            bins_optimal = max(
                5,
                int(n ** 0.5)
            )

        elif value_range <= 0:

            bins_optimal = 1

        else:

            bins_optimal = max(
                3,
                int(
                    value_range
                    / bin_width
                )
            )

        bins_user = (
            self.binSpin.value()
        )

        if bins_user > bins_optimal * 2:

            QMessageBox.information(
                self,
                self.tr("Bins suggestion"),
                self.tr(
                    "You set {0} bins, but the "
                    "recommended value is about {1}."
                ).format(
                    bins_user,
                    bins_optimal
                )
            )

        elif bins_user < bins_optimal / 2:

            QMessageBox.information(
                self,
                self.tr("Bins suggestion"),
                self.tr(
                    "You set only {0} bins, but the "
                    "recommended value is about {1}."
                ).format(
                    bins_user,
                    bins_optimal
                )
            )

    # =================================================================
    # DISPATCH
    # =================================================================

    def _plot_dispatch(
        self,
        fig,
        axes,
        ax2,
        chart_type,
        x_data,
        x_field,
        y_fields,
        y_data_list,
        y2_field,
        y2_data,
        separate_subplots,
        colors,
        color_y2,
        bg_color,
        marker,
        linestyle,
        marker_y2,
        linestyle_y2,
        bins
    ):

        n_series = len(
            y_fields
        )

        if chart_type == "Radar":

            fig.clear()

            self._plot_radar(
                fig,
                y_data_list,
                y_fields
            )

            return

        for index, (
            y_field,
            y_data
        ) in enumerate(
            zip(
                y_fields,
                y_data_list
            )
        ):

            if (
                separate_subplots
                and n_series > 1
                and chart_type not in (
                    "Pie",
                    "Boxplot",
                )
            ):

                ax = axes[index]

            else:

                ax = axes[0]

            series_color = (
                colors[
                    index
                    % len(colors)
                ]
            )

            if chart_type == "Line":

                self._plot_line(
                    ax,
                    x_data,
                    y_data,
                    y_field,
                    series_color,
                    marker,
                    linestyle
                )

            elif chart_type == "Scatter":

                self._plot_scatter(
                    ax,
                    x_data,
                    y_data,
                    y_field,
                    series_color,
                    marker
                )

            elif chart_type == "Bar":

                self._plot_bar(
                    ax,
                    x_data,
                    y_data,
                    y_field,
                    series_color
                )

            elif chart_type == "Histogram":

                self._plot_histogram(
                    ax,
                    y_data,
                    y_field,
                    series_color,
                    bins
                )

            elif chart_type == "Pie":

                if n_series > 1:

                    QMessageBox.warning(
                        self,
                        self.tr("Advanced Charts"),
                        self.tr(
                            "Pie chart supports only one "
                            "Y field at a time."
                        )
                    )

                    fig.clear()

                    return

                self._plot_pie(
                    ax,
                    x_data,
                    y_data
                )

                break

            elif chart_type == "Boxplot":

                self._plot_boxplot(
                    ax,
                    y_data_list,
                    y_fields
                )

                break

            elif chart_type == "Area":

                self._plot_area(
                    ax,
                    x_data,
                    y_data_list,
                    y_fields
                )

                break

            elif chart_type == "Violin":

                self._plot_violin(
                    ax,
                    y_data_list,
                    y_fields,
                    series_color
                )

                break

            elif chart_type == "Linear Regression":

                self._plot_line(
                    ax,
                    x_data,
                    y_data,
                    y_field,
                    series_color,
                    marker,
                    linestyle
                )

                if (
                    self.enableLinearRegressionCheck.isChecked()
                ):

                    self._plot_linear_regression(
                        ax,
                        x_data,
                        y_data,
                        series_color
                    )

            elif chart_type == "Curve Fitting":

                self._plot_line(
                    ax,
                    x_data,
                    y_data,
                    y_field,
                    series_color,
                    marker,
                    linestyle
                )

                fit_type = (
                    self.fitTypeCombo.currentText()
                )

                degree = (
                    self.polyDegreeSpin.value()
                )

                self._plot_curve_fit(
                    ax,
                    x_data,
                    y_data,
                    fit_type,
                    degree,
                    series_color
                )

            ax.set_facecolor(
                bg_color
            )

            if self.gridCheck.isChecked():
                ax.grid(True)

        # -------------------------------------------------------------
        # Y2
        # -------------------------------------------------------------

        if (
            ax2 is not None
            and y2_data is not None
            and chart_type in (
                "Line",
                "Scatter",
                "Linear Regression",
                "Curve Fitting",
            )
        ):

            if chart_type in (
                "Line",
                "Linear Regression",
                "Curve Fitting",
            ):

                self._plot_line(
                    ax2,
                    x_data,
                    y2_data,
                    y2_field,
                    color_y2,
                    marker_y2,
                    linestyle_y2
                )

            elif chart_type == "Scatter":

                self._plot_scatter(
                    ax2,
                    x_data,
                    y2_data,
                    y2_field,
                    color_y2,
                    marker_y2
                )

            ax2.grid(False)

    # =================================================================
    # BASIC PLOTS
    # =================================================================

    def _plot_line(
        self,
        ax,
        x_data,
        y_data,
        label,
        color,
        marker,
        linestyle
    ):

        ax.plot(
            x_data,
            y_data,
            color=color,
            marker=(
                None
                if marker == "None"
                else marker
            ),
            linestyle=(
                None
                if linestyle == "None"
                else linestyle
            ),
            label=label
        )

    # -----------------------------------------------------------------

    def _plot_scatter(
        self,
        ax,
        x_data,
        y_data,
        label,
        color,
        marker
    ):

        selected_marker = (
            "o"
            if marker == "None"
            else marker
        )

        ax.scatter(
            x_data,
            y_data,
            color=color,
            marker=selected_marker,
            label=label
        )

    # -----------------------------------------------------------------

    def _plot_bar(
        self,
        ax,
        x_data,
        y_data,
        label,
        color
    ):

        ax.bar(
            x_data,
            y_data,
            color=color,
            label=label
        )

    # -----------------------------------------------------------------

    def _plot_histogram(
        self,
        ax,
        y_data,
        label,
        color,
        bins
    ):

        ax.hist(
            y_data,
            bins=bins,
            color=color,
            alpha=0.7,
            edgecolor="black",
            linewidth=1.0,
            label=label
        )

    # -----------------------------------------------------------------

    def _plot_pie(
        self,
        ax,
        x_data,
        y_data
    ):

        ax.pie(
            y_data,
            labels=x_data,
            autopct="%1.1f%%"
        )

        ax.set_aspect(
            "equal"
        )

        ax.set_xlabel("")
        ax.set_ylabel("")

        ax.tick_params(
            left=False,
            bottom=False,
            labelleft=False,
            labelbottom=False
        )

    # -----------------------------------------------------------------

    def _plot_boxplot(
        self,
        ax,
        y_data_list,
        y_fields
    ):

        if len(y_data_list) == 1:

            ax.boxplot(
                y_data_list[0],
                labels=[y_fields[0]]
            )

        else:

            ax.boxplot(
                y_data_list,
                labels=y_fields
            )

    # -----------------------------------------------------------------

    def _plot_area(
        self,
        ax,
        x_data,
        y_data_list,
        y_fields
    ):

        x_values = np.asarray(
            x_data
        )

        y_values = np.vstack(
            [
                np.asarray(
                    values,
                    dtype=float
                )
                for values in y_data_list
            ]
        )

        ax.stackplot(
            x_values,
            y_values,
            labels=y_fields
        )

    # =================================================================
    # VIOLIN
    # =================================================================

    def _plot_violin(
        self,
        ax,
        y_data_list,
        y_fields,
        color
    ):

        parts = ax.violinplot(
            y_data_list,
            showmeans=True,
            showmedians=True
        )

        for body in parts["bodies"]:

            body.set_facecolor(
                color
            )

            body.set_edgecolor(
                "black"
            )

            body.set_alpha(
                0.7
            )

        for key in (
            "cbars",
            "cmins",
            "cmaxes",
            "cmeans",
            "cmedians",
        ):

            if key in parts:

                parts[key].set_color(
                    "black"
                )

        ax.set_xticks(
            range(
                1,
                len(y_fields) + 1
            )
        )

        ax.set_xticklabels(
            y_fields
        )

    # =================================================================
    # RADAR
    # =================================================================

    def _plot_radar(
        self,
        fig,
        y_data_list,
        y_fields
    ):

        categories = y_fields

        count = len(
            categories
        )

        values = np.asarray(
            [
                np.mean(
                    np.asarray(
                        values,
                        dtype=float
                    )
                )
                for values in y_data_list
            ],
            dtype=float
        )

        values = np.append(
            values,
            values[0]
        )

        angles = np.linspace(
            0,
            2 * np.pi,
            count,
            endpoint=False
        )

        angles = np.append(
            angles,
            angles[0]
        )

        ax = fig.add_subplot(
            111,
            polar=True
        )

        ax.plot(
            angles,
            values,
            linewidth=2
        )

        ax.fill(
            angles,
            values,
            alpha=0.25
        )

        ax.set_xticks(
            angles[:-1]
        )

        ax.set_xticklabels(
            categories
        )

    # =================================================================
    # LINEAR REGRESSION
    # =================================================================

    def _plot_linear_regression(
        self,
        ax,
        x_data,
        y_data,
        color
    ):

        x_numeric = []

        for value in x_data:

            if isinstance(
                value,
                (
                    datetime.date,
                    datetime.datetime,
                )
            ):

                x_numeric.append(
                    mdates.date2num(
                        [value]
                    )[0]
                )

            else:

                try:

                    x_numeric.append(
                        float(value)
                    )

                except (TypeError, ValueError):

                    return

        x = np.asarray(
            x_numeric,
            dtype=float
        )

        y = np.asarray(
            y_data,
            dtype=float
        )

        if len(x) < 2 or len(y) < 2:
            return

        if len(x) != len(y):
            return

        x0 = x.mean()

        x_normalized = (
            x - x0
        )

        try:

            m, b = np.polyfit(
                x_normalized,
                y,
                1
            )

        except (
            TypeError,
            ValueError,
            np.linalg.LinAlgError,
        ):

            return

        x_fit = np.linspace(
            x_normalized.min(),
            x_normalized.max(),
            200
        )

        y_fit = (
            m * x_fit
            + b
        )

        x_fit_plot = (
            x_fit + x0
        )

        ax.plot(
            x_fit_plot,
            y_fit,
            color=color,
            linestyle="--",
            linewidth=2,
            label=self.tr(
                "Linear regression"
            )
        )

    # =================================================================
    # CURVE FIT
    # =================================================================

    def _plot_curve_fit(
        self,
        ax,
        x_data,
        y_data,
        fit_type,
        degree,
        color
    ):

        try:

            from scipy.optimize import curve_fit

        except ImportError:

            QMessageBox.warning(
                self,
                self.tr("Advanced Charts"),
                self.tr(
                    "SciPy is required for curve fitting."
                )
            )

            return

        x = np.asarray(
            x_data,
            dtype=float
        )

        y = np.asarray(
            y_data,
            dtype=float
        )

        if len(x) < 2:
            return

        if len(x) != len(y):
            return

        if fit_type == "Polynomial":

            try:

                coeffs = np.polyfit(
                    x,
                    y,
                    degree
                )

            except (
                TypeError,
                ValueError,
                np.linalg.LinAlgError,
            ):

                return

            polynomial = np.poly1d(
                coeffs
            )

            x_fit = np.linspace(
                np.min(x),
                np.max(x),
                200
            )

            y_fit = polynomial(
                x_fit
            )

        elif fit_type == "Exponential":

            def exponential_function(
                value,
                a,
                b
            ):
                return (
                    a
                    * np.exp(
                        b * value
                    )
                )

            try:

                params, _ = curve_fit(
                    exponential_function,
                    x,
                    y,
                    maxfev=10000
                )

            except (
                TypeError,
                ValueError,
                RuntimeError,
            ):

                return

            x_fit = np.linspace(
                np.min(x),
                np.max(x),
                200
            )

            y_fit = exponential_function(
                x_fit,
                *params
            )

        elif fit_type == "Logarithmic":

            if np.any(x <= 0):
                return

            def logarithmic_function(
                value,
                a,
                b
            ):
                return (
                    a
                    + b
                    * np.log(value)
                )

            try:

                params, _ = curve_fit(
                    logarithmic_function,
                    x,
                    y,
                    maxfev=10000
                )

            except (
                TypeError,
                ValueError,
                RuntimeError,
            ):

                return

            x_fit = np.linspace(
                np.min(x),
                np.max(x),
                200
            )

            y_fit = logarithmic_function(
                x_fit,
                *params
            )

        elif fit_type == "Power":

            if np.any(x <= 0):
                return

            def power_function(
                value,
                a,
                b
            ):
                return (
                    a
                    * value ** b
                )

            try:

                params, _ = curve_fit(
                    power_function,
                    x,
                    y,
                    maxfev=10000
                )

            except (
                TypeError,
                ValueError,
                RuntimeError,
            ):

                return

            x_fit = np.linspace(
                np.min(x),
                np.max(x),
                200
            )

            y_fit = power_function(
                x_fit,
                *params
            )

        else:

            QMessageBox.warning(
                self,
                self.tr("Advanced Charts"),
                self.tr(
                    "Unknown fit type."
                )
            )

            return

        ax.plot(
            x_fit,
            y_fit,
            color=color,
            linestyle="--",
            linewidth=2,
            label=self.tr(
                "{0} fit"
            ).format(
                fit_type
            )
        )

    # =================================================================
    # SAVE
    # =================================================================

    def save_plot(self):

        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Save chart"),
            "",
            "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf)"
        )

        if not path:
            return

        try:

            self.figure.savefig(
                path,
                dpi=300,
                bbox_inches="tight"
            )

        except (
            OSError,
            ValueError,
            RuntimeError,
        ) as exc:

            QMessageBox.warning(
                self,
                self.tr("Advanced Charts"),
                self.tr(
                    "Error saving image:\n{0}"
                ).format(
                    str(exc)
                )
            )

    # =================================================================
    # UTILITIES
    # =================================================================

    def _safe_float_list(
        self,
        values
    ):

        output = []

        for value in values:

            try:

                output.append(
                    float(value)
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

        return output

    # -----------------------------------------------------------------

    def _safe_numeric(
        self,
        value
    ):

        try:

            return float(value)

        except (
            TypeError,
            ValueError,
        ):

            return None
