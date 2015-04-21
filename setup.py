from setuptools import setup, find_packages
setup(name='fah_reseeder',
      version='1.0',
 packages=find_packages(),
  entry_points={'console_scripts':
              ['fah_reseeder = fah_reseeder.fah_reseed:reseed_project']}
#py_modules=['fah_reseed']
	#py_modules=['fah_reseed','convert_project','featurize_project','cluster_project','reseed_project'],
      )
