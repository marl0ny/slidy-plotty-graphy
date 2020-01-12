# Copyright (C) 2020 Mark (marl0ny)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Main Qt App.

Issues:
 -When moving the plot view or zooming in or out 
 the plot likes to flicker.
 -When rescaling the plot, some
 artefacts may appear along the right edge of the plot.
 -The quality of the plot may worsen as one zoomes out.
 This is caused by the number of sampling points of the function
 being fixed and finite.

Features to add:
 -Get the location of the mouse pointer.
 -Make it possible to adjust the number of ticks
 and the range of the sliders through the GUI.
 -Add a settings button to each of the parameter sliders.
 This produces a popup where one can change the number of ticks
 or change the range.
"""
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from plotty_animation import PlottyAnimator
from typing import Any, Tuple, Union
from numpy import linspace


class Canvas(FigureCanvasQTAgg):
    """
    The canvas.
    """

    def __init__(self, parent: QtWidgets.QMainWindow, rect: QtCore.QRect) -> None:
        """
        The constructor.

        Parameters:
         rect: used to get information
         about the screen width and screen height.
        """
        width = rect.width()
        dpi = int(150*width//1920)
        figsize = (4, 4)
        interval = int(1000/60)
        self._ani = PlottyAnimator(dpi, figsize, interval)
        FigureCanvasQTAgg.__init__(self, self._ani.figure)
        self.setMinimumHeight(400)
        self._DIFF = 0
        self._ANTIDIFF = 1
        self._TITLE = 2
        self._menu_dict = {"Differentiate w.r.t. x": self._DIFF, 
                           "Antidifferentiate w.r.t. x": self._ANTIDIFF,
                           "Substitute title "
                           "parameters with values": self._TITLE}
        self._menu_list = [key for key in self._menu_dict]
        self._menu = QtWidgets.QMenu(parent)
        self._menu.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        for item in self._menu_list:
            self._menu.addAction(item)
        self._menu.triggered.connect(self.on_right_click_popup)
        self._MOUSE_DEFAULT_ACTION = 0
        self._MOUSE_MOVE_PLOT = 1
        self._MOUSE_EDIT_FUNCTION = 2
        self._mouse_usage = self._MOUSE_MOVE_PLOT
        self._prev_mouse_position = []

    def _mouse_coordinates_transform(self, 
                                     x: int, y: int) -> Tuple[float, float]:
        """
        Transform the location of the mouse as expressed in terms
        of the coordinates of the GUI window into the coordinates
        of the plot.

        Parameters:
         x: x location of mouse
         y: y location of mouse

        Returns:
         A tuple containing the transformed x and y coordinates.
        """
        ax = self.figure.get_axes()[0]
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        pixel_xlim = [ax.bbox.xmin, ax.bbox.xmax]
        pixel_ylim = [ax.bbox.ymin, ax.bbox.ymax]
        height = self.figure.bbox.ymax
        mx = (xlim[1] - xlim[0])/(pixel_xlim[1] - pixel_xlim[0])
        my = (ylim[1] - ylim[0])/(pixel_ylim[1] - pixel_ylim[0])
        x = (x - pixel_xlim[0])*mx + xlim[0]
        y = (height - y - pixel_ylim[0])*my + ylim[0]
        return x, y


    def _mouse_handler(self, qt_event: QtGui.QMouseEvent) -> None:
        """
        Mouse handling helper function.

        Parameters:
         qt_event: mouse event.
        """
        x = qt_event.x()
        y = qt_event.y()
        if qt_event.buttons() == QtCore.Qt.LeftButton:
            if (self._mouse_usage == self._MOUSE_MOVE_PLOT
                or self._mouse_usage == self._MOUSE_DEFAULT_ACTION):
                x, y = self._mouse_coordinates_transform(x, y)
                if self._prev_mouse_position != []:
                    x_prev, y_prev = self._prev_mouse_position
                    dx = x - x_prev
                    dy = y - y_prev
                    # self.setCursor()
                    self._ani.move_axes(self._ani.figure.get_axes()[0],
                                        -dx, -dy)
                    self._ani.on_plot_view_changed()
                else:
                    self._prev_mouse_position = [x, y]
            elif self._mouse_usage == self._MOUSE_EDIT_FUNCTION:
                x, y = self._mouse_coordinates_transform(x, y)
                self._ani.change_values(x, y)
        if qt_event.buttons() == QtCore.Qt.MidButton:
            pass
        if qt_event.buttons() == QtCore.Qt.RightButton:
            pass

    def on_right_click_popup(self, action: QtWidgets.QAction) -> None:
        """
        Perform an action when one selects from the right click popup.

        Parameters:
         action: action that occured when one clicked on one of the
         options on the right click menu.
        """
        action_val = self._menu_dict[action.text()]
        print(action_val)
        if action_val == self._DIFF:
            self._ani.differentiate_function()
        elif action_val == self._ANTIDIFF:
            self._ani.antidifferentiate_function()
        elif action_val == self._TITLE:
            pass

    def set_mouse_usage(self, usage: int) -> None:
        """
        Set how the mouse should be used.

        Parameters:
         usage: the mouse usage number.
        """
        self._mouse_usage = usage

    def mousePressEvent(self, qt_event: QtGui.QMouseEvent) -> None:
        """
        Mouse is pressed.

        Parameters:
         qt_event: mouse event.
        """
        if qt_event.buttons() == QtCore.Qt.RightButton:
            self._menu.popup(self.mapToGlobal(qt_event.pos()))
            # if not self._menu.isTearOffEnabled():
            #     self._menu.setTearOffEnabled(True)
            #     self._menu.popup(qt_event.pos())
            #     # self._menu.showTearOffMenu()
            # else:
            #     self._menu.setTearOffEnabled(False)
        x, y = self._mouse_coordinates_transform(qt_event.x(), qt_event.y())
        self._prev_mouse_position = [x, y]
        self._mouse_handler(qt_event)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, qt_event: QtGui.QMouseEvent) -> None:
        """
        Mouse is moved.

        Parameters:
         qt_event: mouse event.
        """
        self._mouse_handler(qt_event)

    def mousePressRelease(self, qt_event: QtGui.QMouseEvent) -> None:
        """
        Mouse is released.

        Parameters:
         qt_event: mouse event.
        """
        self.setMouseTracking(False)

    def wheelEvent(self, qt_event: QtGui.QWheelEvent) -> None:
        """
        The mouse wheel is moved.

        Parameters:
         qt_event: mouse wheel event.
        """
        scroll_val = qt_event.angleDelta().y()
        ax = self._ani.figure.get_axes()[0]
        if scroll_val == 120:
            self._ani.scale_axes(ax, 0.9, 0.9)
            self._ani.on_plot_view_changed()
        elif scroll_val == -120:
            self._ani.scale_axes(ax, 1.1, 1.1)
            self._ani.on_plot_view_changed()

    def get_animation(self) -> PlottyAnimator:
        """
        Getter for the animation object.

        Returns:
         The animation object.
        """
        return self._ani

    def animation_loop(self) -> None:
        """
        Do the main animation loop.
        """
        self._ani.animation_loop()


class Slider(QtWidgets.QSlider):
    """
    Slider class
    """

    def __init__(self, slider_id: Any,
                 orientation: QtCore.Qt.Orientation,
                 context: Any) -> None:
        """
        Constructor.

        Parameters:
         slider_id: slider identification.
         orientation: slider orientation.
         context: the object that is using this slider.
        """
        QtWidgets.QSlider.__init__(self, orientation, context)
        self._slider_id = slider_id
        self._observers = []
        self._lim = [self.minimum(), self.maximum()]
        self.setRange(0, 200)
        self.valueChanged.connect(self.notify_change)

    def set_observers(self, slider_observers: list) -> None:
        """
        Set slider observers.

        Parameters:
         slider_observers: the objects that will observe this slider.
        """
        self._observers = slider_observers

    def set_number_of_ticks(self, number_of_ticks: int) -> None:
        """
        Set the total number of intervals in the slider.

        Parameters:
         number_of_ticks: total number of intervals.
        """
        self.setRange(1, number_of_ticks)

    def set_range(self, min_val: float, max_val: float) -> None:
        """
        Set the range of the slider.

        Parameters:
         min_val: The lowest possible value that the slider can take.
         max_val: The largest possible value that the slider can take.
        """
        self._lim = [min_val, max_val]

    def _transform(self, slider_val: int) -> float:
        """
        Transform rules for the slider.
        """
        lim = self._lim
        slider_val = slider_val - self.minimum()
        m = (lim[1] - lim[0])/(self.maximum() - self.minimum())
        return m*slider_val + lim[0]

    def set_slider(self, value: float) -> None:
        """
        Set a value for the slider.

        Parameters:
         value: the value to set the slider to.
        """
        lim = self._lim
        value = value - lim[0]
        m = (self.maximum() - self.minimum())/(lim[1] - lim[0])
        self.setSliderPosition(int(m*value + self.minimum()))

    def notify_change(self, val: int) -> None:
        """
        Notify to observers that the slider has changed.

        Parameters:
         val: the value that the slider changed to.
        """
        val = self._transform(val)
        for observer in self._observers:
            observer.on_slider_changed({'value': val,
                                       'id': self._slider_id})

    def get_slider_info(self) -> dict:
        """
        Get information about the slider.

        Returns:
         A dictionary containing information about the slider.
        """
        val = self.value()
        val = self._transform(val)
        return {'value': val, 'id': self._slider_id}


class HorizontalSliderBox(QtWidgets.QGroupBox):
    """
    GUI Box containing a slider as well as some other widgets.
    """
    def __init__(self, context: Any,
                 slider_id: Any) -> None:
        """
        Constructor.

        Parameters:
         context: the object that is using the widget.
         slider_id: the id of the slider.
        """
        QtWidgets.QGroupBox.__init__(self)
        self.setMinimumWidth(250)
        self.setMaximumWidth(300)
        self.setMaximumHeight(100)
        self._layout = QtWidgets.QVBoxLayout()
        self._label = QtWidgets.QLabel("Set " + str(slider_id))
        self._slider = Slider(slider_id,
                              QtCore.Qt.Horizontal,
                              context)
        self._layout.addWidget(self._label)
        self._layout.addWidget(self._slider)
        self.setLayout(self._layout)

    def set_range(self, min_val: float, max_val: float) -> None:
        """
        Set the range of the slider.

        Parameters:
         min_val: The lowest possible value that the slider can take.
         max_val: The largest possible value that the slider can take.
        """
        self._slider.set_range(min_val, max_val)

    def set_number_of_ticks(self, number_of_ticks: int) -> None:
        """
        Set the total number of intervals in the slider.

        Parameters:
         number_of_ticks: total number of intervals.
         """
        self._slider.setRange(0, number_of_ticks - 1)

    def set_slider(self, value: float) -> None:
        """
        Set a value for the slider.

        Parameters:
         value: the value to set the slider to.
        """
        self._slider.set_slider(value)

    def set_observers(self,
                      slider_observers: list) -> None:
        """
        Set slider observers.

        Parameters:
         slider_observers: the objects that will observe the slider.
        """
        slider_observers.append(self)
        self._slider.set_observers(slider_observers)

    def on_slider_changed(self, slider_input: dict) -> None:
        """
        Respond to changes in the slider.

        Parameters:
         slider_input: the changes from the slider.
        """
        val = slider_input['value']
        slider_id = slider_input['id']
        self._label.setText("%s = %.2f" % (slider_id, val))

    def destroy_slider(self) -> None:
        """
        Destroy the slider.
        """
        self._layout.removeWidget(self._slider)
        self._slider.destroy()
        self._slider.close()
        self.close()

    def get_slider_info(self) -> dict:
        """
        Get information about the slider.

        Returns:
         A dictionary containing information about the slider.
        """
        return self._slider.get_slider_info()


class HorizontalEntryBox(QtWidgets.QGroupBox):
    """
    GUI Box that contains an label and text input widget.
    """

    def __init__(self, label_name: str) -> None:
        """
        Constructor.

        Parameters:
         label_name: the label for the entry widget.
        """
        QtWidgets.QGroupBox.__init__(self)
        self.setMinimumWidth(250)
        self.setMaximumWidth(300)
        self.setMaximumHeight(125)
        self._observers = []
        self._label = QtWidgets.QLabel(label_name)
        self._layout = QtWidgets.QVBoxLayout()
        self._input = QtWidgets.QLineEdit()
        self._input.returnPressed.connect(self.notify_change)
        self._button = QtWidgets.QPushButton("OK")
        self._button.clicked.connect(self.notify_change)
        self._layout.addWidget(self._label)
        self._layout.addWidget(self._input)
        self._layout.addWidget(self._button)
        self.setLayout(self._layout)

    def set_observers(self, observers: list) -> None:
        """
        Set the observers for the line edit widget.

        Parameters:
         observers: The observers of the widget.
        """
        self._observers = observers

    def notify_change(self) -> None:
        """
        Notify to the observers that the line edit has changed
        """
        for observer in self._observers:
            observer.on_entry_returned(
                self._input.text())


class App(QtWidgets.QMainWindow):
    """
    Main qt5 app.
    """

    def __init__(self) -> None:
        """
        Initializer.
        """
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("A simple GUI")
        self.sliders = []
        self.window = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QHBoxLayout(self.window)
        rect = QtWidgets.QApplication.desktop().screenGeometry()
        self.canvas = Canvas(self, rect)
        colorname = self.window.palette().color(
                QtGui.QPalette.Background).name()
        self.canvas.get_animation().figure.patch.set_facecolor(colorname)
        self.layout.addWidget(self.canvas)
        self.control_widgets = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.control_widgets)
        self._build_control_widgets()
        self.setCentralWidget(self.window)
        self.canvas.animation_loop()

    def _build_control_widgets(self):
        """
        Build the control widgets.
        """
        self.entry = HorizontalEntryBox(
            "Set function f(x)")
        self.mouse_dropdown = QtWidgets.QComboBox(self)
        self.mouse_dropdown.addItems(["Mouse: ",
                                      "Move plot view",
                                      "Edit function"])
        self.mouse_dropdown.activated.connect(self.on_mouse_dropdown_changed)
        self.dropdown_dict = {"sin": "a*sin(k*(x - phi)) + c",
                              "cos": "a*cos(k*(x - phi)) + c",
                              "tan": "a*tan(k*(x - phi)) + c",
                              "arcsin": "a*arcsin(k*(x - phi)) + c",
                              "arccos": "a*arccos(k*(x - phi)) + c",
                              "arctan": "a*arcsin(k*(x - phi)) + c",
                              "sinh": "a*sinh(k*(x - b)) + c",
                              "cosh": "a*cosh(k*(x - b)) + c",
                              "tanh": "a*tanh(k*x) + c",
                              "exp": "c1*exp(-x*k1) + c2*exp(x*k2) + c",
                              "log": "a*log(k*(x - b)) + c",
                              "power": "a**x + c",
                              # "power2": "a*(x - b)**p + c",
                              "quadratic": "a*x**2 + b*x + c",
                              "gaussian": 
                              "a*exp(-((x-u)/sigma)**2/2)/(sqrt(pi*sigma**2))",
                              "wavepacket": 
                              "a*sin(2*pi*k*x)*"
                              "exp(-((x-mu)/sigma)**2/2)/(sqrt(pi*sigma**2))",
                         }
        dropdown_list = ["Set Preset f(x): "]                
        dropdown_list.extend([key for key in self.dropdown_dict])
        self.dropdown = QtWidgets.QComboBox(self)
        self.dropdown.addItems(dropdown_list)
        if hasattr(self.dropdown, "textActivated"):
            self.dropdown.textActivated.connect(self.on_dropdown_changed)
        else:
            self.dropdown.activated.connect(self.on_dropdown_changed)
        self.entry.set_observers([self])
        self.control_widgets.addWidget(self.mouse_dropdown)
        self.control_widgets.addWidget(self.dropdown)
        self.control_widgets.addWidget(self.entry)

    def on_dropdown_changed(self, text: Union[int, str]) -> None:
        """
        Perform an action when the dropdown is changed.

        Parameters:
         text: either the index of the dropdown or text
         at the given index of the dropdown.
        """
        if isinstance(text, str):
            if not text == "Set Preset f(x): ":
                self.set_function_from_text(self.dropdown_dict[text])
        elif isinstance(text, int):
            n = text
            text = self.dropdown.itemText(n)
            if not text == "Set Preset f(x): ":
                self.set_function_from_text(self.dropdown_dict[text])

    def on_mouse_dropdown_changed(self, index: int) -> None:
        """
        Perform an action when the mouse dropdown is changed.

        Parameters:
         index: the index of the dropdown.
        """
        self.canvas.set_mouse_usage(index)

    def set_function_from_text(self, text: str) -> None:
        """
        Set the function from text.

        Parameters:
         text: function expressed as a string.
        """
        self.destroy_sliders()
        function_name = text
        ani = self.canvas.get_animation()
        ani.set_function(function_name)
        dictionary = ani.function.get_default_values()
        for key in dictionary:
            slider_box = HorizontalSliderBox(self, key)
            self.control_widgets.addWidget(slider_box)
            slider_box.set_observers([self])
            slider_box.set_range(-10.0, 10.0)
            slider_box.set_number_of_ticks(201)
            slider_box.set_slider(dictionary[key])
            self.sliders.append(slider_box)

    def on_slider_changed(self, slider_input: dict) -> None:
        """
        When the slider is changed perform some action.

        Parameters:
         slider_input: a dictionary containing information
         about the slider.
        """
        d = {}
        if self.sliders != []:
            for slider in self.sliders:
                info = slider.get_slider_info()
                d[info['id']] = info['value']
            default_values = tuple([d[key] for key in d])
            # print(default_values)
            ani = self.canvas.get_animation()
            ani.set_parameters(default_values)

    def destroy_sliders(self) -> None:
        """
        Destroy the sliders.
        """
        while self.sliders != []:
            slider_box = self.sliders.pop()
            self.control_widgets.removeWidget(slider_box)
            self.layout.removeWidget(slider_box)
            slider_box.destroy_slider()
            slider_box.close()

    def on_entry_returned(self, text: str) -> None:
        """
        Perform an action when the enter function is pressed.

        Parameters:
         text: a string from an entry box.
        """
        self.set_function_from_text(text)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    qtapp = QtWidgets.QApplication(sys.argv)
    app = App()
    app.show()
    sys.exit(qtapp.exec_())
