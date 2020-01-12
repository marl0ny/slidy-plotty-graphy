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
Abstract animation class and constants.
"""
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib.collections import Collection, PathCollection
from matplotlib.quiver import QuiverKey, Quiver
import matplotlib.animation as animation
from typing import List, Tuple
from time import perf_counter


artists = [Line2D, Collection, Text, QuiverKey, Quiver, PathCollection]


class Animator:
    """
    Abstract animation class that adds a small layer of abstraction
    over the matplotlib animation functions and interfaces.

    To use this class:
    -Inherit this in a derived class.
    -The Figure object is already instantiated in this class as the
     attribute self.figure. Create instances of
     plotting objects from this, such as Line2D.
    -Update the plots inside the update method, which must be
     overriden.
    -Call the animation_loop method to show the animation.

    Attributes:
     figure [Figure]: Use this to obtain plot elements.
    """

    def __init__(self, dpi: int,
                 figsize: Tuple[int], animation_interval: int) -> None:
        """
        The initializer.

        Parameters:
         dpi: dots per inches, which controls the resolution.
         fisize: tuple of two ints, which sets the size of the plot.
         animation_interval: set the animation interval in milliseconds
         between each animation frame.
        """
        self.dots_per_inches = dpi
        self.animation_interval = animation_interval

        self.figure = plt.figure(
                figsize=figsize,
                dpi=self.dots_per_inches
        )
        self.main_animation = None

        # All private attributes.
        self._plots = []
        self._delta_t = 1.0/60.0
        self._t = perf_counter()

    def add_plot(self, plot: plt.Artist) -> None:
        """
        Add a list of plot objects so that they can be animated.

        Parameters:
         plot: a plot that can be animated.
        """
        self._plots.append(plot)

    def add_plots(self, plot_objects: List[plt.Artist]) -> None:
        """
        Add multiple plots to be animated.

        Parameters:
         plot_objects: list of plot objects that can be animated.
        """
        self._plots.extend(plot_objects)

    def update(self, delta_t: float) -> None:
        """
        Update how each plots will change between each animation frame.
        This must be implemented in any derived classes.

        Parameters:
         delta_t: amount of time in seconds between each animation frame.
        """
        raise NotImplementedError

    def _make_frame(self, i: int) -> list:
        """
        Generate a single animation frame.
        """
        self.update(self._delta_t)
        t = perf_counter()
        self._delta_t = t - self._t
        self._t = t
        # print(self._plots)
        return self._plots

    def _add_plots(self) -> None:
        """
        Add plots before doing the main animation loop.
        """
        text_objects = []  # Ensure that text boxes are rendered last
        self_dict = self.__dict__
        for key in self_dict:
            if any([isinstance(self_dict[key], artist) for
                    artist in artists]):
                if self_dict[key] not in self._plots:
                    # Ensure that text boxes are rendered last
                    if isinstance(self_dict[key], Text):
                        text_objects.append(self_dict[key])
                    else:
                        self._plots.append(self_dict[key])
        self._plots.extend(text_objects)

    def animation_loop(self) -> None:
        """This method plays the animation. This must be called in order
        for an animation to be shown.
        """
        self._add_plots()
        self.main_animation = animation.FuncAnimation(
                self.figure,
                self._make_frame,
                blit=True,
                interval=self.animation_interval,
                init_func=lambda *arg: []
        )

    def toggle_blit(self) -> None:
        """
        If the animation is blitted remove the blitting,
        otherwise add blitting to the animation. 
        This is used so that it is possible to update the appearance of the 
        plot title and axes, which would otherwise
        be entirely static with blitting.
        """
        # TODO: Find a better way of updating the axes of the plot
        # that uses blitting and does not access the
        # protected members of the Animation class.
        if self.main_animation._blit:
            self.main_animation._blit_clear(
                self.main_animation._drawn_artists, 
                self.main_animation._blit_cache)
            self.main_animation._blit = False
        else:
            # self.main_animation._init_draw()
            self.main_animation._step()
            self.main_animation._blit = True
            self.main_animation._setup_blit()

    def flush(self):
        self.main_animation._blit_clear(
                self.main_animation._drawn_artists, 
                self.main_animation._blit_cache)
        self.main_animation._step()
    
    def scale_axes(self, ax, 
                   x_scale_factor: float,
                   y_scale_factor: float) -> None:
        """
        Enlarge or reduce the range of the axes of the plots,
        with respect to the centre of the plot.

        Parameters:
         ax: the AxesSubplot object to modify. 
         x_scale_factor [float]: scale the x axes.
         y_scale_factor [float]: scale the y axes.
        """
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        dx = xlim[1] - xlim[0]
        dy = ylim[1] - ylim[0]
        xc = (xlim[1] + xlim[0])/2
        yc = (ylim[1] + ylim[0])/2
        xlim = [xc - x_scale_factor*dx/2.0, xc + x_scale_factor*dx/2.0]
        ylim = [yc - y_scale_factor*dy/2.0, yc + y_scale_factor*dy/2.0]
        self.toggle_blit()
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        self.toggle_blit()

    def move_axes(self, ax, 
                  move_by_x: float, move_by_y: float) -> None:
        """
        Translate the x and y axes.

        Parameters:
         ax: the AxesSubplot object to modify.
         move_by_x [float]: translation value for the x axis.
         move_by_y [float]: translation value for the y axis.
        """
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        xlim = [xlim[0] + move_by_x,
                xlim[1] + move_by_x]
        ylim = [ylim[0] + move_by_y,
                ylim[1] + move_by_y]
        self.toggle_blit()
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        self.toggle_blit()
