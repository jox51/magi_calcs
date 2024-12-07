from setuptools import Extension
from Cython.Build import cythonize

def build(setup_kwargs):
    extensions = [
        Extension(
            "astro_charts.transit_calculator",
            ["astro_charts/transit_calculator.pyx"],
        )
    ]
    
    setup_kwargs.update({
        "ext_modules": cythonize(
            extensions,
            compiler_directives={
                "language_level": "3",
                "boundscheck": False,
                "wraparound": False,
            }
        ),
        "zip_safe": False,
    })