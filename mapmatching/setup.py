from distutils.core import setup
setup(name='mapmatcher',
      version='1.0',
      packages=['mapmatcher'],
      package_dir={'mapmatcher': 'mapmatcher'}, requires=['networkx','osmapi','overpass','sympy']
      )