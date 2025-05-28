from setuptools import setup

setup(name='geobleu',
      version='0.4',
      description='Implementation of GEO-BLEU and other evaluation metrics for HuMob Challenge',
      url='https://github.com/yahoojapan/geobleu',
      author='Toru Shimizu, LY Corporation',
      author_email='toshimiz@lycorp.co.jp',
      license='MIT',
      install_requires=['numpy', 'scipy'],
      packages=['geobleu'],
      zip_safe=False)
