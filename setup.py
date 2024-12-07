from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        "astro_charts.transit_calculator",
        ["astro_charts/transit_calculator.pyx"],
    )
]

setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            "language_level": "3",
            "boundscheck": False,
            "wraparound": False,
        }
    )
)