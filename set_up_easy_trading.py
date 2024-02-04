from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Package to trade with python on mt5 plataform'
LONG_DESCRIPTION = 'This package provides a series of methods and attributues to make easier the building and deployment of python trading bots'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="Easy_Trading", 
        version=VERSION,
        author="Sebastián Ospina Valencia",
        author_email="thequanttrader123@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['MetaTrader5','bs4', 'datetime'],
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3",
            "Operating System :: Microsoft :: Windows",
        ]
)