import numpy as np
import math

import sys
sys.path.append('..')

from plotting import LinkedPlot

x_axis = tuple(float(x / 10) for x in range(100))
y1_axis = tuple(math.sin(x) for x in x_axis)
y2_axis = tuple(math.cos(x) for x in x_axis)

matrix = np.array(list(zip(x_axis, y1_axis, y2_axis)),
                  dtype=[('date', 'f8'),
                         ('y1', 'f8'),
                         ('y2', 'f8')])

linked_plot = LinkedPlot(window_title="LOL Window")
linked_plot.add_plot(plot_title="LOL Plot1")
linked_plot.add_subplot(matrix, y_axis_name='y1')
linked_plot.add_subplot(matrix, y_axis_name='y2')
linked_plot.add_plot(plot_title="LOL Plot2")
linked_plot.add_subplot(matrix, y_axis_name='y1')
linked_plot.add_marker("LOL Plot1", "y2", x_axis[10], text="LOL")
linked_plot.show()
