import sys
from PyQt6.QtCore import Qt, QRectF, QLineF, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen
from PyQt6.QtWidgets import QApplication, QWidget, QSizePolicy

class MultiSlider(QWidget):
    LEFT_MARGIN = 10
    RIGHT_MARGIN = 10
    POINT_DIAMETER = 10
    TRACK_COLOR = QColor(20, 240, 240)
    POINT_COLOR = QColor(255, 255, 255)
    TRACK_THICKNESS = 2
    DEFAULT_SIZE = QSize(200, 20)

    def __init__(self, min_value=0.0, max_value=1.0, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.min_value = min_value
        self.max_value = max_value
        # List of points' X-axis coordinates scaled in [min_value; max_value] range
        self.points = []
        self.selected_point = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw slider track
        track_line = QLineF(self.LEFT_MARGIN, self.height() / 2, self.width() - self.RIGHT_MARGIN, self.height() / 2)
        painter.setPen(QPen(self.TRACK_COLOR, self.TRACK_THICKNESS))
        painter.drawLine(track_line)

        # Draw points
        for point in self.points:
            x = self.get_denormalized_x(point)
            y = self.height() / 2
            painter.setBrush(QBrush(self.POINT_COLOR))
            painter.drawEllipse(QRectF(x - self.POINT_DIAMETER / 2,
                                       y - self.POINT_DIAMETER / 2,
                                       self.POINT_DIAMETER,
                                       self.POINT_DIAMETER))

    def mousePressEvent(self, event):
        """Handle left-click - selecting and creating points; handle right-click - removing points.
        """
        x = event.position().x()

        # Check if clicked on existing point
        self.selected_point = self.is_on_point(x)
        # Left-click handling
        if (event.button() == Qt.MouseButton.LeftButton):
            # If left-clicked on existing point, do nothing
            if (self.selected_point is not None):
                return
            # Else add new point
            else:
                new_point = self.get_scaled_x(x)
                self.points.append(new_point)
                # Immediately select new point (which is last in list of points)
                # This overcomes the need to release mouse and click again
                self.selected_point = len(self.points) - 1
        # Right-click handling
        elif (event.button() == Qt.MouseButton.RightButton):
            if (self.selected_point is not None):
                self.points.pop(self.selected_point)
                self.selected_point = None
        self.update()

    def mouseMoveEvent(self, event):
        if self.selected_point is not None:
            x = event.position().x()
            new_value = self.get_scaled_x(x)
            self.points[self.selected_point] = max(self.min_value, min(self.max_value, new_value))
            self.update()

    def mouseReleaseEvent(self, event):
        self.selected_point = None

    def is_on_point(self, x):
        """Return point's index if x is close to some point's X coordinate.
        
        Args:
            x (int): x coordinate on slider track.
        Returns:
            i (int): index of close point.
        """
        threshold = 5
        for i, point in enumerate(self.points):
            px = self.get_denormalized_x(point)
            if abs(px - x) < threshold:
                return i
        return None

    def get_denormalized_x(self, scaled_x):
        """Calculate point X coordinate to display on window from scaled point X coordinate.
        
        Args:
            scaled_x (float): scaled point X coordinate.
        Returns:
            x (float): point X coordinate to display on window.
        """
        normalized_x = (scaled_x - self.min_value) / (self.max_value - self.min_value)
        x = self.LEFT_MARGIN + normalized_x * (self.width() - self.LEFT_MARGIN - self.RIGHT_MARGIN)
        return x

    def get_scaled_x(self, x):
        """Normalize and scale X coordinate acquired from window to range [self.min_value; self.max_value].
        
        Args:
            x (int): coordinate of range [0; self.width()].
        Returns:
            scaled_x (float): coordinate normalized and scaled to range [self.min_value; self.max_value].
        """
        scaled_x = self.min_value + (x - self.LEFT_MARGIN) \
                                   / (self.width() - self.LEFT_MARGIN - self.RIGHT_MARGIN) \
                                   * (self.max_value - self.min_value)
        return scaled_x

    def get_selected_value(self):
        print(round(self.points[self.selected_point], 2))
        return self.points[self.selected_point]

    def sizeHint(self):
        return self.DEFAULT_SIZE 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    slider = MultiSlider()
    slider.show()
    sys.exit(app.exec())
