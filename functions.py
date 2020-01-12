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
functions.py
"""
import numpy as np
from sympy import lambdify, abc, latex, diff, integrate
from sympy.parsing.sympy_parser import parse_expr
from sympy.core import basic
from typing import Dict, List, Union, Callable


class VariableNotFoundError(Exception):
    """Variable not found error.
    """
    def __str__(self) -> None:
        """Print this exception.
        """
        return "Variable not found"

def zero(x: Union[np.ndarray, float], 
        *args: float) -> float:
    """
    Map to zero.

    Parameters:
     x: input value
     *args: additional input values

    Returns:
     The value 0.
    """
    return 0.0

def rect(x: 
         Union[
         np.ndarray, float]) -> Union[np.ndarray, float]:
    """
    Rectangle function. Defined as
     rect(x) = 1 if x^2 <= 1 else 0

    Parameters:
     x: input values.

    Returns
     rect(x)
    """
    if isinstance(x, np.ndarray):
        y = [(1.0 if x[i]**2 <= 1.0 else 0.0) 
            for i in range(len(x))]
        y = np.array(y)
    elif isinstance(x, float):
        y = 1.0 if x**2 <= 1.0 else 0.0
    return y


def is_defined_at_values(f: Callable, 
                         *args: float, **kw: float) -> bool:
    """
    Check if a function is actually defined at
    a given values.

    Parameters:
     f: The function to check
     args: arguments of the function
     kw: same as args, but with keyword arguments.

    Returns:
     Whether the function is actually defined or not.
    """
    try:
        f(*args, **kw)
    except Exception as e:
        print(e)
        return False
    return True


def multiplies_var(main_var: basic.Basic, arb_var: basic.Basic,
                   expr: basic.Basic) -> bool:
    """
    This function takes in the following parameters:
    main_var [sympy.core.basic.Basic]: the main variable
    arb_var [sympy.core.basic.Basic]: an arbitrary variable
    expr [sympy.core.basic.Basic]: an algebraic expression
    Check to see if an arbitrary variable multiplies
    a sub expression that contains the main variable.
    If it does, return True else False.

    The following examples should clarify what this function does:

    >>> expr = parse_expr("a*sinh(k*x) + c")
    >>> multiplies_var(abc.x, abc.a, expr)
    True
    >>> multiplies_var(abc.x, abc.k, expr)
    True
    >>> multiplies_var(abc.x, abc.b, expr)
    False

    >>> expr = parse_expr("w*a**pi*sin(k**10*tan(y*x)*z) + d + e**10*tan(f)")
    >>> multiplies_var(abc.x, abc.w, expr)
    True
    >>> multiplies_var(abc.x, abc.a, expr)
    True
    >>> multiplies_var(abc.x, abc.k, expr)
    True
    >>> multiplies_var(abc.x, abc.z, expr)
    True
    >>> multiplies_var(abc.x, abc.y, expr)
    True
    >>> multiplies_var(abc.x, abc.d, expr)
    False
    >>> multiplies_var(abc.x, abc.e, expr)
    False
    >>> multiplies_var(abc.x, abc.f, expr)
    False

    >>> expr = parse_expr("a*sinh(x*(b**2 + 45.0*c)) + d")
    >>> multiplies_var(abc.x, abc.a, expr)
    True
    >>> multiplies_var(abc.x, abc.b, expr)
    True
    >>> multiplies_var(abc.x, abc.c, expr)
    True
    >>> multiplies_var(abc.x, abc.d, expr)
    False
    """
    arg_list = []
    for arg1 in expr.args:
        if arg1.has(main_var):
            arg_list.append(arg1)
            for arg2 in expr.args:
                if ((arg2 is arb_var or (arg2.is_Pow and arg2.has(arb_var)))
                   and expr.has(arg1*arg2)):
                    return True
    return any([multiplies_var(main_var, arb_var, arg)
                for arg in arg_list if
                (arg is not main_var)])


# class FunctionRtoNone:
#     """
#     """
#     def __init__(self) -> None:
#         """
#         """
#         pass
#
#     def __call__(self, param1, param2, *args):
#         return np.zeros([])


class FunctionRtoR:
    """
    A callable function class that maps a single variable,
    as well as any number of parameters, to another variable.

    Attributes:
    latex_repr [str]: The function as a LaTeX string.
    symbols [sympy.Symbol]: All variables used in this function.
    parameters [sympy.Symbol]: All variables used in this function,
                               except for the main variable.
    """

    # Private Attributes:
    # _symbolic_func [sympy.basic.Basic]: symbol function
    # _lambda_func [sympy.Function]: lamba function

    def __init__(self, function_name: str, param: basic.Basic) -> None:
        """
        The initializer. The parameter must be a
        string representation of a function, and it needs to
        be a function of x.
        """
        # Dictionary of modules and user defined functions.
        # Used for lambdify from sympy to parse input.
        module_list = ["numpy", {"rect": rect, "zeros": zero}]
        self._symbolic_func = parse_expr(function_name)
        symbol_set = self._symbolic_func.free_symbols
        symbol_list = list(symbol_set)
        if param not in symbol_list:
            raise VariableNotFoundError
        self.latex_repr = latex(self._symbolic_func)
        symbol_list.remove(param)
        self.parameters = symbol_list
        var_list = [param]
        var_list.extend(symbol_list)
        self.symbols = var_list
        self._lambda_func = lambdify(
            self.symbols, self._symbolic_func, modules=module_list)

    def __call__(self, x: Union[np.array, float],
                 *args: float, **kwargs: float) -> np.array:
        """
        Call this class as if it were a function.
        """
        if args == ():
            kwargs = self.get_default_values()
            args = (kwargs[s] for s in kwargs)
        return self._lambda_func(x, *args, **kwargs)

    def __str__(self) -> str:
        """
        string representation of the function.
        """
        return str(self._symbolic_func)

    def get_function_name(self) -> str:
        """
        Get the name of the function.
        """
        return str(self._symbolic_func)

    def _reset_samesymbols(self) -> None:
        """
        Set to a new function, assuming the same variables.
        """
        self.latex_repr = latex(self._symbolic_func)
        self._lambda_func = lambdify(
            self.symbols, self._symbolic_func)

    def get_default_values(self) -> Dict[basic.Basic, float]:
        """
        Get a dict of the suggested default values for each parameter
        used in this function.
        """
        return {s:
                float(multiplies_var(self.symbols[0], s, self._symbolic_func))
                for s in self.parameters}

    def derivative(self) -> None:
        """
        Mutate this function into its derivative.

        >>> f = FunctionRtoR("a*sin(k*x) + d", abc.x)
        >>> f.derivative()
        >>> str(f)
        'a*k*cos(k*x)'
        """
        self._symbolic_func = diff(self._symbolic_func,
                                   self.symbols[0])
        self._reset_samesymbols()

    def antiderivative(self) -> None:
        """
        Mutate this function into its antiderivative.

        >>> f = FunctionRtoR("a*sin(k*x) + d", abc.x)
        >>> f.antiderivative()
        >>> str(f)
        'a*Piecewise((-cos(k*x)/k, Ne(k, 0)), (0, True)) + d*x'
        """
        self._symbolic_func = integrate(self._symbolic_func,
                                        self.symbols[0])
        self._reset_samesymbols()


if __name__ == "__main__":
    import doctest
    from time import perf_counter
    t1 = perf_counter()
    doctest.testmod()
    t2 = perf_counter()
    print(t2 - t1)
