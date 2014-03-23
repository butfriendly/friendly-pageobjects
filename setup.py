from setuptools import setup, find_packages, Command


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

setup(name='friendly-selenium-pageobjects',
      version='1.0.3',
      description='Basement for selenium tests based on the pageobject-pattern',
      long_description='',
      author='ButFriendly',
      author_email='hello@butfriendly.com',
      license='3-Clause BSD',
      url='',
      include_package_data=True,
      classifiers=[],
      namespace_packages=['friendly'],
      packages=find_packages(exclude=['tests']),
      install_requires=['selenium==2.37.0',
                        'pyyaml>=3.10'],
      cmdclass={'test': PyTest},)
