import csv
import sys
from pathlib import Path

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
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

        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
        layout.addWidget(self.canvas)

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
        if selected_data:
            axis.plot(
                months,
                [selected_data[month] for month in months],
                marker="o",
                label="Loaded data",
            )
        if reference_data:
            axis.plot(months, reference_values, marker="o", label="Tel Aviv reference")
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
            "Monthly Rainfall Comparison" if selected_data else "Monthly Rainfall"
        )
        axis.set_xlabel("Month")
        axis.set_ylabel("Rainfall (mm)")
        axis.grid(True, alpha=0.3)
        if axis.lines:
            axis.legend()
        self.figure.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RainfallComparisonApp()
    window.show()
    sys.exit(app.exec())
