from distutils.core import setup

setup(
    name='git_data_mining',
    version='3.5',
    packages=[''],
    url='https://github.com/IKARion/git_data_mining',
    license='MIT',
    author='Yassin',
    author_email='taskin@collide.info',
    description='Mines file changes from git repos and writes to an xapi store',
    install_requires=["GitPython"],
)
