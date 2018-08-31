from setuptools import setup


setup(
    name='pwm',
    version='0.1',
    py_modules=['pwm'],
    install_requires=[
        'Click'
    ],
    entry_points='''
      [console_scripts]
      pwm=pwm:cli  
    '''
)