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

import numpy as np
import matplotlib.pyplot as plt
from animator import Animator
from functions import FunctionRtoR, is_defined_at_values, VariableNotFoundError
from sympy import abc
from typing import Tuple, List
import config


def change_array(x_arr: np.ndarray, y_arr: np.ndarray,
                 x: float, y: float) -> np.ndarray:
    """
    Given a location x that maps to a value y,
    and an array x_arr which maps to array y_arr, find the closest
    element in x_arr to x. Then, change its corresponding
    element in y_arr with y.
    """

    if (x < x_arr[0]) or (x > x_arr[-1]):
        return y_arr
    # if (y < y_arr[0]) or (y > y_arr[-1]):
    #     return y_arr

    closest_index = np.argmin(np.abs(x_arr - x))
    y_arr[closest_index] = y

    # If len(x) is large, change nearby values as well.
    if (len(x_arr) > 100):
        try:
            for i in range(3):
                y_arr[closest_index + i] = y
                y_arr[closest_index - i] = y
        except IndexError:
            pass

    return y_arr


class PlottyAnimator(Animator):

    def __init__(self, dpi: int, 
                 figsize: Tuple[int], interval: int) -> None:
        """
        The constructor.

        Parameters:
         dpi: dots per inches, which controls the resolution.
         fisize: tuple of two ints, which sets the size of the plot.
         animation_interval: set the animation interval in milliseconds
         between each animation frame.
        """
        Animator.__init__(self, dpi, figsize, interval)
        ax = self.figure.add_subplot(1, 1, 1)
        # self.t = np.linspace(-np.pi, np.pi, 256)
        if "Number of points" in config.config:
            n = config.config["Number of points"]
            self.t = np.linspace(-np.pi, np.pi, n)
        else:
            self.t = np.linspace(-np.pi, np.pi, 1024)
        ax.grid()
        if "function" in config.config:
            f = config.config["function"]
            self.function = FunctionRtoR(f, abc.x)
            ax.set_title("f(x) = %s" % (f))
        else:
            self.function = FunctionRtoR("sin(x)", abc.x)
            ax.set_title("f(x) = sin(x)")
        default_values = self.function.get_default_values()
        self.params = (default_values[key] for key in default_values)
        self.y = self.function(self.t, *self.params)
        ax.set_xlim(np.amin(self.t), np.amax(self.t))
        ax.set_xlabel("x")
        if "Plot Colour" in config.config:
            color = config.config["Plot Colour"]
            line, = ax.plot(self.t, self.y, color=color)
        else:
            line, = ax.plot(self.t, self.y)
        self.line = line

    def update(self, delta_t: float) -> None:
        """
        Override the update method of the Animator class.

        Parameters:
         delta_t: time interval passed between each frame.
        """
        self.line.set_ydata(self.y)

    def change_values(self, x: float, y: float) -> None:
        """
        Change the values of the function output array to y
        at the specified location on the input array x.

        Parameters:
         x: x value that corresponds to the new y value.
         y: new y value
        """
        change_array(self.t, self.y, x, y)

    def set_parameters(self, parameters: List[float]) -> None:
        """
        Set the parameters used for the function.

        Parameters:
         parameters: the parameters of the function.
        """
        try:
            # print(parameters)
            y = self.function(self.t, *parameters)
        except TypeError as e:
            # if there is a float division by
            # zero maybe set the parameter to one?
            print(e)
            return
        self.params = tuple(parameters)
        self.y = y

    def on_plot_view_changed(self) -> None:
        """
        Respond if the plot view is changed.
        """
        xlim = self.figure.get_axes()[0].get_xlim()
        n = len(self.t)
        # print(xlim)
        self.t = np.linspace(xlim[0], xlim[1], n)
        self.line.set_xdata(self.t)
        self.y = self.function(self.t, *self.params)

    def set_title(self, function_name: str) -> None:
        """
        Setter for the title of the plot.

        Parameters:
         function_name: the name of the function.
        """
        self.toggle_blit()
        ax = self.figure.get_axes()[0]
        if "&" in function_name or len(function_name) > 150:
            ax.set_title("f(x)")
        else:
            ax.set_title(r"%s" %(function_name))
        # ax.set_title(r"%s" %(function_name))
        self.toggle_blit()

    def differentiate_function(self) -> None:
        """
        Differentiate the function.
        """
        old_function_name = self.function.get_function_name()
        self.function.derivative()
        self._diff_helper(old_function_name)

    def antidifferentiate_function(self) -> None:
        """
        Antidifferentiate the function.
        """
        old_function_name = self.function.get_function_name()
        self.function.antiderivative()
        self._diff_helper(old_function_name)

    def _diff_helper(self, old_function_name: str) -> None:
        """
        Helper function for the both the differentiation
        and antidifferentiation functions.

        Parameters:
         old_function_name: the name of the original function
         before mutating it to its derivative or antiderivative.
        """
        d = self.function.get_default_values()
        params = tuple(d[key] for key in d)
        if not is_defined_at_values(self.function, np.pi, *params):
            self.set_function(old_function_name)
            return
        self.set_title("$f(x) = %s$" % self.function.latex_repr)
        self.y = self.function(self.t, 
                          *self.params)

    def set_function(self, function_name: str) -> None:
        """
        Setter for the function.

        Parameters:
         function_name: the string name of the function.
        """
        if function_name.strip() == "":
            function_name == "zero(x)"
        if function_name != ():
            try:
                function = FunctionRtoR(function_name, abc.x)
            except Exception as e:
                print(e)
                return
            d = function.get_default_values()
            params = tuple(d[key] for key in d)
            if not is_defined_at_values(function, np.pi, *params):
                return
            self.set_title("$f(x) = %s$" % function.latex_repr)
            self.params = params
            self.function = function
            # print(default_values)
            self.y = function(self.t, 
                              *self.params)
