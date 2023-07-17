from setuptools import setup

setup(name='geobleu',
      version='0.2',
      description='Implementation of GEO-BLEU and other evaluation metrics for HuMob Challenge 2023',
      url='http://github.com/storborg/funniest',
      author='Toru Shimizu, Yahoo Japan Corporation',
      author_email='toshimiz@yahoo-corp.jp',
      license='MIT',
      install_requires=['numpy', 'scipy'],
      packages=['geobleu'],
      zip_safe=False)
