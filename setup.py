import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 0):
    raise RuntimeError('Python 2 not supported')
if sys.version_info < (3, 2):
    raise RuntimeError('Python 3.0-3.1 not supported because ' +
                       'typing module is not available')

with open('./requirements.txt') as txt:
        requirements = [line for line in txt]

with open('./test-requirements.txt') as txt:
        test_requirements = [line for line in txt]

setup(
    name='nmzswarm',
    version='0.0.1',
    packages=find_packages(),
    scripts=['bin/nmzswarm'],
    install_requires=requirements,
    tests_require=test_requirements,
    author='Akihiro Suda',
    author_email='suda.akihiro@lab.ntt.co.jp',
    description='CI Job Parallelizer built on Kubernetes/Docker',
    license='Apache License 2.0',
    keywords=['docker'],
    url='https://github.com/osrg/namazu-swarm',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Clustering'
        'Topic :: Software Development :: Testing',
        'Operating System :: POSIX :: Linux',
    ],
)
