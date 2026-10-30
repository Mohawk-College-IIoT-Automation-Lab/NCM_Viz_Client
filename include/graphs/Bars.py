from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget
import pyqtgraph as pg


class SignedBarWidget(QWidget):
    """A single signed horizontal bar growing left or right from a zero line.

    Instantaneous only - there is no rolling buffer. Each call to SetValue
    replaces the bar rather than appending to a history.
    """

    class SignedBar(pg.PlotWidget):

        def __init__(
            self,
            v_min: float = -5.0,
            v_max: float = 5.0,
            color: str = "#ff0000",
            bar_thickness: float = 0.6,
            parent=None,
        ):
            super().__init__(parent)

            self._v_min = v_min
            self._v_max = v_max

            self.plotItem.showGrid(x=True, y=False, alpha=0.5)
            self.plotItem.setXRange(v_min, v_max, padding=0)
            self.plotItem.setYRange(-0.5, 0.5, padding=0)
            self.plotItem.disableAutoRange()
            self.plotItem.hideAxis("left")
            self.plotItem.hideButtons()
            self.plotItem.setMouseEnabled(False, False)
            self.plotItem.setMenuEnabled(False)

            self._zero_line = pg.InfiniteLine(
                pos=0.0, angle=90, pen=pg.mkPen("#aaaaaa", width=1)
            )
            self.plotItem.addItem(self._zero_line)

            self._bar = pg.BarGraphItem(
                x0=[0.0],
                x1=[0.0],
                y=[0.0],
                height=[bar_thickness],
                brush=pg.mkBrush(color),
                pen=pg.mkPen(None),
            )
            self.plotItem.addItem(self._bar)

            self.setMinimumSize(120, 90)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        @pyqtSlot(float)
        def SetValue(self, value: float) -> float:
            clamped = max(self._v_min, min(self._v_max, float(value)))
            self._bar.setOpts(x1=[clamped])
            return clamped

        @pyqtSlot()
        def ClearBar(self):
            self._bar.setOpts(x1=[0.0])

    def __init__(
        self,
        title: str = "Title",
        title_size: int = 20,
        units: str = "m/s",
        v_min: float = -5.0,
        v_max: float = 5.0,
        color: str = "#ff0000",
        label_color: str = "#ffffff",
        value_size: int = 18,
        decimals: int = 2,
        parent=None,
    ):
        super().__init__(parent)

        self._decimals = decimals
        self._units = units

        self._bar = SignedBarWidget.SignedBar(v_min, v_max, color)

        self._title_label = QLabel(title)
        self._title_label.setAlignment(Qt.AlignCenter)
        self._title_label.setStyleSheet(
            f"font-size: {title_size}px; color: {label_color}"
        )

        self._value_label = QLabel(self._format(0.0))
        self._value_label.setAlignment(Qt.AlignCenter)
        self._value_label.setStyleSheet(
            f"font-size: {value_size}px; color: {label_color}"
        )

        v_box = QVBoxLayout()
        v_box.addWidget(self._title_label)
        v_box.addWidget(self._bar)
        v_box.addWidget(self._value_label)
        self.setLayout(v_box)

    def _format(self, value: float) -> str:
        return f"{value:.{self._decimals}f} {self._units}"

    @pyqtSlot(float)
    def SetValue(self, value: float):
        clamped = self._bar.SetValue(value)
        self._value_label.setText(self._format(clamped))

    @pyqtSlot()
    def ClearBar(self):
        self._bar.ClearBar()
        self._value_label.setText(self._format(0.0))


class GroupedBarWidget(QWidget):
    """Grouped vertical bar chart: N bar sets across M labelled categories.

    Bars are drawn from y_min upward, so the chart reads correctly on an axis
    that does not start at zero (e.g. 950-1200 mbar).
    """

    class GroupedBar(pg.PlotWidget):

        def __init__(
            self,
            categories,
            set_count: int,
            colors,
            y_min: float = 0.0,
            y_max: float = 100.0,
            y_label: str = "label",
            y_label_size: int = 18,
            bar_width: float = 0.32,
            group_gap: float = 0.04,
            parent=None,
        ):
            super().__init__(parent)

            self._categories = list(categories)
            self._y_min = y_min
            self._y_max = y_max

            self.plotItem.setLabel(
                "left",
                f'<span style="font-size: {y_label_size}px">{y_label}</span>',
            )
            self.plotItem.showGrid(x=False, y=True, alpha=0.5)
            self.plotItem.setYRange(y_min, y_max, padding=0)
            self.plotItem.setXRange(-0.6, len(self._categories) - 0.4, padding=0)
            self.plotItem.disableAutoRange()
            self.plotItem.hideButtons()
            self.plotItem.setMouseEnabled(False, False)
            self.plotItem.setMenuEnabled(False)

            x_positions = list(range(len(self._categories)))
            self.plotItem.getAxis("bottom").setTicks(
                [list(zip(x_positions, self._categories))]
            )

            pitch = bar_width + group_gap
            self._bars = []
            for s in range(set_count):
                offset = (s - (set_count - 1) / 2.0) * pitch
                bar = pg.BarGraphItem(
                    x=[x + offset for x in x_positions],
                    height=[0.0] * len(x_positions),
                    width=bar_width,
                    y0=[y_min] * len(x_positions),
                    brush=pg.mkBrush(colors[s]),
                    pen=pg.mkPen(None),
                )
                self.plotItem.addItem(bar)
                self._bars.append(bar)

            self.setMinimumSize(200, 200)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        def SetSet(self, set_index: int, values):
            heights = [
                max(self._y_min, min(self._y_max, float(v))) - self._y_min
                for v in values
            ]
            self._bars[set_index].setOpts(height=heights)

        @pyqtSlot()
        def ClearBars(self):
            zeros = [0.0] * len(self._categories)
            for bar in self._bars:
                bar.setOpts(height=zeros)

    def __init__(
        self,
        categories,
        set_labels,
        title: str = "Title",
        title_size: int = 24,
        y_label: str = "label",
        y_label_size: int = 18,
        y_min: float = 0.0,
        y_max: float = 100.0,
        colors=("#ff0000", "#e6c200"),
        label_size: int = 18,
        bar_width: float = 0.32,
        height: int = 200,
        parent=None,
    ):
        super().__init__(parent)

        self._set_labels = list(set_labels)

        self._plot = GroupedBarWidget.GroupedBar(
            categories,
            len(self._set_labels),
            colors,
            y_min,
            y_max,
            y_label,
            y_label_size,
            bar_width,
        )
        self._plot.setMinimumHeight(height)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"font-size: {title_size}px; color: #ffffff")

        legend_h_box = QHBoxLayout()
        for label, color in zip(self._set_labels, colors):
            swatch = QLabel(label)
            swatch.setStyleSheet(f"font-size: {label_size}px; color: {color}")
            legend_h_box.addWidget(swatch)
        legend_h_box.addStretch(1)

        v_box = QVBoxLayout()
        v_box.addWidget(title_label)
        v_box.addWidget(self._plot)
        v_box.addLayout(legend_h_box)
        self.setLayout(v_box)

    def SetSet(self, set_index: int, values):
        self._plot.SetSet(set_index, values)

    def SetByLabel(self, set_label: str, values):
        self._plot.SetSet(self._set_labels.index(set_label), values)

    @pyqtSlot()
    def ClearBars(self):
        self._plot.ClearBars()
