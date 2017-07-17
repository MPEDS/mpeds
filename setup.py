from distutils.core import setup

setup(
    name = 'MPEDS',
    packages = ['mpeds'],
    version = '0.1',
    author = 'Alex Hanna',
    author_email = 'alex.hanna@utoronto.ca',
    package_data = {'mpeds': ['tokenizers/*.jar', 'classifiers/*.pkl', 'classifiers/*.ser.gz', 'input/*.csv']},
    include_package_data = True
)
