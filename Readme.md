# A Rudimentary Plotting Application

This project is intended to be a simple real-time interactive desktop plotting app built primarily using [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5), [Matplotlib](https://matplotlib.org/), [Sympy](https://www.sympy.org/en/index.html), and [Numpy](https://numpy.org/).

To obtain this program first ensure that you have the latest version of Python with PyQt5, Matplotlib, Sympy, and Numpy installed. These may be installed using `pip3 install PyQt5 numpy matplotlib sympy`. Then download or clone this repository, and run the file `qtapp.py`.

## Instructions
Drag the plot around to change the plot view. Zoom in and out using the mouse wheel. To use the mouse to edit the appearance of the function, go to the mouse dropdown and select 'Edit function'. To plot a new function, enter a new function in the 'Set function f(x)' entry box or choose a preset function in the 'Set preset f(x)' dropdown menu. Please note, the function that you enter must at least be a function of x. All other variables become parameters that you can vary using the sliders.

## License
Since PyQt5 is published under [GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html), this project is put under the same license as well.