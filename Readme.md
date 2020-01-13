# A Rudimentary Plotting Application

This project is intended to be a simple real-time interactive desktop plotting app built primarily using [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5), [Matplotlib](https://matplotlib.org/), [Sympy](https://www.sympy.org/en/index.html), and [Numpy](https://numpy.org/).
I made this project so that I could learn how to use Qt in Python and integrate it with matplotlib, so that I can eventually reimplement some of my Tkinter projects in Qt Python.

To obtain this program first ensure that you have the latest version of Python with PyQt5, Matplotlib, Sympy, and Numpy installed. These may be installed using `pip3 install PyQt5 numpy matplotlib sympy`. Then download or clone this repository, and run the file `qtapp.py`.

## Instructions

<img src="https://raw.githubusercontent.com/marl0ny/slidy-plotty-graphy/master/demo.gif" />

Drag the plot around to change the plot view. Use the mouse wheel for zooming in or out. To plot a new function, enter a new function in the 'Set function f(x)' entry box or choose a preset function in the 'Set preset f(x)' dropdown menu. The function that you enter must at least be a function of x. You may additionally enter other variables as well, which become parameters that you vary using the sliders.

## License
Since PyQt5 is published under [GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html), this project is put under the same license as well.
