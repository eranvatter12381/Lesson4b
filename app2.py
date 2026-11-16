import csv
import math
import sys
from pathlib import Path

from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT,
)
from matplotlib.figure import Figure
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class RainfallComparisonApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rainfall Data Comparison")
        self.resize(800, 600)
        self.filename = ""

        self.load_button = QPushButton("LOAD DATA")
        self.load_button.clicked.connect(self.load_data)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        reference_path = Path(__file__).resolve().parent / "tel_aviv_rainfall.csv"
        try:
            reference_data = self._read_rainfall_data(reference_path)
        except (OSError, ValueError, csv.Error) as error:
            self.statusBar().showMessage(f"Reference data unavailable: {error}")
            self.compare_data({}, {})
        else:
            self.compare_data({}, reference_data)

    def load_data(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select rainfall data",
            "",
            "CSV files (*.csv);;All files (*)",
        )
        if not filename:
            return

        self.filename = filename
        try:
            selected_data = self._read_rainfall_data(Path(self.filename))
            reference_path = Path(__file__).resolve().parent / "tel_aviv_rainfall.csv"
            reference_data = self._read_rainfall_data(reference_path)
            self.compare_data(selected_data, reference_data)
        except (OSError, ValueError, csv.Error) as error:
            QMessageBox.critical(self, "Unable to load data", str(error))

    @staticmethod
    def _read_rainfall_data(path):
        with path.open("r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            required_columns = {"Month", "Rainfall_mm"}
            if not reader.fieldnames or not required_columns.issubset(reader.fieldnames):
                raise ValueError(
                    f"{path.name} must contain Month and Rainfall_mm columns."
                )

            data = {}
            for row in reader:
                month = (row.get("Month") or "").strip()
                try:
                    rainfall = float(row["Rainfall_mm"])
                except (TypeError, ValueError) as error:
                    raise ValueError(
                        f"{path.name} contains an invalid rainfall value."
                    ) from error
                if not month:
                    raise ValueError(f"{path.name} contains a row without a month.")
                data[month] = rainfall

        if not data:
            raise ValueError(f"{path.name} contains no rainfall data.")
        return data

    def compare_data(self, selected_data, reference_data):
        months = list(selected_data or reference_data)
        reference_values = [reference_data.get(month) for month in months]

        self.figure.clear()
        axis = self.figure.add_subplot(111)
        self.figure.set_facecolor("#f4f6f8")
        axis.set_facecolor("#ffffff")
        positions = list(range(len(months)))
        if selected_data and reference_data:
            bar_width = 0.4
            axis.bar(
                [position - bar_width / 2 for position in positions],
                [selected_data[month] for month in months],
                bar_width,
                color="#3572a5",
                label="Loaded data",
            )
            axis.bar(
                [position + bar_width / 2 for position in positions],
                [
                    value if value is not None else math.nan
                    for value in reference_values
                ],
                bar_width,
                color="#e08b36",
                label="Tel Aviv reference",
            )
        elif selected_data:
            axis.bar(
                positions,
                [selected_data[month] for month in months],
                0.7,
                color="#3572a5",
                label="Loaded data",
            )
        elif reference_data:
            axis.bar(
                positions,
                reference_values,
                0.7,
                color="#e08b36",
                label="Tel Aviv reference",
            )
        if positions:
            axis.set_xticks(positions, months)
        if not selected_data and not reference_data:
            axis.text(
                0.5,
                0.5,
                "Load a CSV file to display rainfall data.",
                ha="center",
                va="center",
                transform=axis.transAxes,
            )
        axis.set_title(
            "Monthly Rainfall Comparison" if selected_data else "Monthly Rainfall",
            fontsize=14,
            fontweight="bold",
            pad=14,
        )
        axis.set_xlabel("Month", labelpad=8)
        axis.set_ylabel("Rainfall (mm)", labelpad=8)
        axis.set_axisbelow(True)
        axis.grid(axis="y", linestyle="--", linewidth=0.7, alpha=0.35)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.margins(y=0.12)
        if axis.containers:
            axis.legend(frameon=False)
        self.figure.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RainfallComparisonApp()
    window.show()
    sys.exit(app.exec())
