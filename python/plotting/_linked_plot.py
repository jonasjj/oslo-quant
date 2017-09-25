import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg
from setproctitle import setproctitle
import datetime
import numpy as np
import signal

class LinkedPlotWidget(pg.GraphicsLayoutWidget):
    """Widget for stacking several plots with linked x-axes vertically"""

    mouse_pressed_signal = QtCore.pyqtSignal()
    mouse_released_signal = QtCore.pyqtSignal()

    def __init__(self, inputs, window_title=''):
        """
        args:
           inputs: list of tuples: (numpy_array, data_column_name, plot_title).
                   It is assumed that numpy_array['date'] exists.
           window_title(str): Title of the window
        """
        super().__init__()

        self.setWindowTitle(window_title)

        # label for showing y/x values for crosshair
        self.label = pg.LabelItem(justify='left')
        self.label.setVisible(True)
        self.addItem(self.label)

        # strings for construction self.label, used by self.update_label()
        self.cursor_x_label = ''
        self.cursor_y_label = ''

        # install an event filter to detect that the mouse leaves the widget
        self.installEventFilter(self)

        self.plot_row_counter = 1
        self.first_plot = None
        self.plots = {}

        # create initial plots
        for numpy_array, data_column_name, plot_title in inputs:
            self.add_plot(numpy_array, data_column_name, plot_title)

            self.show()

    def add_plot(self, numpy_array, data_column_name, plot_title):
        """
        Replace plots with new data

        args:
           It is assumed that numpy_array['date'] exists.
        """
        # if the plot title already exists
        if plot_title in self.plots:
            raise Exception("The plot title '%s' already exists" % plot_title)
        
        pl = self.addPlot(row=self.plot_row_counter, col=0, title=plot_title,
                          y=numpy_array[data_column_name], x=numpy_array['date'])
        self.plots[plot_title] = pl
        self.plot_row_counter += 1

        # link the x-axes of all plots
        if self.first_plot:
            box = pl.getViewBox()
            box.setXLink(self.first_plot)
        else:
            self.first_plot = pl.getViewBox()

        # set fixed tick label width, to that the plots align vertically
        pl.getAxis('left').setWidth(60)

        # crosshair
        v_line = pg.InfiniteLine(angle=90, movable=False)
        h_line = pg.InfiniteLine(angle=0, movable=False)
        pl.addItem(v_line, ignoreBounds=True)
        pl.addItem(h_line, ignoreBounds=True)

        # vertical line for showing the time position of an event
        event_line = pg.InfiniteLine(angle=90, movable=False)
        event_line.setPen(QtGui.QColor(168, 34, 3))
        pl.addItem(event_line, ignoreBounds=True)

        pl.scene().sigMouseMoved.connect(self.mouse_moved)

        # store references to these things in the PlotView object
        pl.v_line = v_line
        pl.h_line = h_line
        pl.event_line = event_line

        # the text responsible for showing the y value where the vertival line is
        value_text = pg.TextItem(anchor=(0.5,0))
        value_text.setPos(92,0)
        value_text.setParentItem(pl)
        pl.value_text = value_text

        # hide meaningless x-axis ticks
        pl.getAxis('bottom').setTicks([])

    def remove_plot(self, plot_title):
        pl = self.plots.pop(plot_title)
        self.removeItem(pl)

    def remove_all_plots(self):
        for pl_title in list(self.plots):
            self.remove_plot(pl_title)
        self.first_plot = None

    def add_marker(self, plot_title, date, angle=-90, text="", color='blue'):
        """
        Add a marker to a plot
        
        Args:
           plot_title (str): The plot title to add a marker to
           date (datetime.date): x-axis date to add a marker to
           angle (int): Angle of the arrow marker. -90 is top down.
           color (str): 'blue', 'green', or 'red'

        Raises:
           IndexError: If the date isn't present in the data set
        """        
        # get the plot
        pl = self.plots[plot_title]

        # convert date to timestamp
        timestamp = datetime.datetime(date.year, date.month, date.day).timestamp()

        ld = pl.listDataItems()[0]
        
        # get the index containing the nearest timestamp value for this x position
        x_data = ld.getData()[0]
        matches = np.where(x_data == timestamp)[0]

        # if this happens, there is something wrong with the data
        if len(matches) > 1:
            raise Exception("There are more than one x index containing this timestamp")

        elif len(matches) < 1:
            raise IndexError("The timestamp " + str(date) + " wasn't found in the data set")

        else:
            x_index = matches[0]

        # a curvepoint refers to an xy point on the plot line
        curvePoint = pg.CurvePoint(ld, index=x_index)

        # background color
        if color == 'blue':
            brush = (0, 0, 255, 110) # blue
        elif color == 'green':
            brush = (0, 255, 0, 110) # green
        elif color == 'red':
            brush = (255, 0, 0, 150) # red
        else:
            raise Exception("Color '%s' isn't implemented" % color)

        # create an arrow
        arrow = pg.ArrowItem(angle=angle, brush=brush)
        arrow.setParentItem(curvePoint)

        if text != "":
            
            # split into <span> tags
            spans = []
            for line in text.split("\n"):
                spans.append('<span style="color: #FF0; font-size: 14pt;">%s</span>' % line)

            # create html text box
            html = '<div style="text-align: center">%s</div>' % "<br>".join(spans)

            # Adjust the y anchor point to the number of lines in the text box.
            # I don't know how to so this properly.
            if len(spans) == 1:
                anchor_y = 1.8
            elif len(spans) == 2:
                anchor_y = 1.45
            elif len(spans) == 3:
                anchor_y = 1.32
            elif len(spans) == 4:
                anchor_y = 1.25
            elif len(spans) == 5:
                anchor_y = 1.2
            else:
                raise Exception("%d line count text box isn't implemented" % anchor_y)

            # create the text box and attach it to the curve point
            text = pg.TextItem(html=html, anchor=(0.5,anchor_y), border='w', fill=brush)
            text.setParentItem(curvePoint)

        pl.addItem(curvePoint)

    def leaveEvent(self, event):
        """Called when the mouse leaves this widget"""
        self.crosshair_visible(False)
        self.hide_label()

    def vertical_line(self, timestamp):
        """Draw a vertical line at timestamp"""

        for plot in self.plots.values():
            # get a reference to the x-axis numpy data (time column)
            time_col = plot.dataItems[0].xData

            plot.event_line.setPos(timestamp)
            plot.event_line.setVisible(True)

    def crosshair_visible(self, true_or_false):
        """Set closshair visibility"""
        for pl in self.plots.values():
            pl.h_line.setVisible(true_or_false)
            pl.v_line.setVisible(true_or_false)

    def update_label(self, cursor_x, cursor_y):
        """Change the labels. Arguments are floats"""
        timestamp = datetime.date.fromtimestamp(cursor_x)
        timestamp_str = timestamp.strftime("%Y-%m-%d")
        text = "<span>crosshair</span>: " \
               "<span style='color: Aqua'>x=%s</span>, " \
               "<span style='color: GreenYellow'>y=%s</span>" % (timestamp_str, str(round(cursor_y, 4)))
        self.label.setText(text)

    def hide_label(self):
        """Hide labels"""
        self.label.setText('')

    def mouse_moved(self, pos):
        """Callback when mouse is moved"""
        mouse_is_over_a_plot = False

        for pl in self.plots.values():
            # ignore plots that are invisible
            if not pl.isVisible():
                continue

            try:
                mousePoint = pl.vb.mapSceneToView(pos)
            except np.linalg.LinAlgError:
                # probably, the plot was replaced, causing this error
                return

            # if the mouse pointer is over this plot
            if pl.sceneBoundingRect().contains(pos):
                mouse_is_over_a_plot = True
                pl.h_line.setVisible(True)
                pl.h_line.setPos(mousePoint.y())
                self.update_label(cursor_x=mousePoint.x(), cursor_y=mousePoint.y())
            else:
                pl.h_line.setVisible(False)

            # set the position of the vertical line
            pl.v_line.setPos(mousePoint.x())

        # if the mouse pointer is over any of the plots
        if mouse_is_over_a_plot:
            for pl in self.plots.values():
                pl.v_line.setVisible(True)
                
                # get the x position of the vertical crosshair line
                x_mouse = mousePoint.x()

                # get the numpy arrays containing the x and y data for this plot
                ld = pl.listDataItems()[0]
                data = ld.getData()
                x_data = data[0]
                y_data = data[1]

                # get the index containing the nearest timestamp value for this x position
                x_index = (np.abs(x_data - x_mouse)).argmin()

                # if the x index is at the min position
                if x_index == 0:

                    # hide the text if the x position outside of the plot
                    if x_mouse < x_data[0]:
                        pl.value_text.setText("")

                # if the x index is at the max position
                elif x_index == len(x_data) - 1:

                    # hide the text if the x position outside of the plot
                    if x_mouse > x_data[-1]:
                        pl.value_text.setText("")

                # if the x position is within the plot
                else:
                    # get the y value
                    y = y_data[x_index]
                
                    # set the y value at the vertical line on this plot at the x position
                    text = "<span style='color: GreenYellow'>y=%s</span>" % str(round(y, 4))
                    pl.value_text.setHtml(text)
                
        else:
            # hide the crosshair text
            self.hide_label()

            # hide the plot y value text
            for pl in self.plots.values():
                pl.value_text.setText("")

    def eventFilter(self, widget, event):
        # if the mouse pointer exits the widget
        if event.type() == QtCore.QEvent.MouseMove:
            self.hide_label()
            for pl in self.plots.values():
                pl.h_line.setVisible(False)
                pl.v_line.setVisible(False)
        return False

    def mousePressEvent(self,event):
        super().mousePressEvent(event)
        self.mouse_pressed_signal.emit()

    def mouseReleaseEvent(self,event):
        super().mouseReleaseEvent(event)
        self.mouse_released_signal.emit()

def linked_plot(inputs, window_title=''):
    """Create a windows of linked plots using LinkedPlotWidget

        args:
           inputs: list of tuples: (numpy_array, data_column_name, plot_title).
                   It is assumed that numpy_array['date'] exists.
           window_title(str): Title of the window
    """
    setproctitle("nordnetbot-linkedplot")
    app = QtWidgets.QApplication(sys.argv)
    lw = LinkedPlotWidget(inputs, window_title)

    # install signal handler
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    sys.exit(app.exec_())
