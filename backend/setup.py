from setuptools import find_packages, setup

from eeg_web_assistant import __version__

setup(
    name='eeg_web_assistant',
    version=__version__,
    packages=find_packages(),
    install_requires=[
        'celery[redis]==4.4.7',
        'fastapi==0.61.1',
        'mne==0.21.0',
        'networkx==2.5',
        'numpy==1.18.1',
        'PyYAML==5.3.1',
        'passlib[bcrypt]==1.7.4',
        'plotly==4.12.0',
        'pydantic[email]==1.6.1',
        'pymongo==3.11.0',
        'python-jose[cryptography]==3.2.0',
        'python-multipart==0.0.5',
        'scipy==1.4.1',
        'spektral==0.6.2',
        'tensorflow==2.3.0',
        'uvicorn==0.11.8',
        'yasa==0.3.0',
    ],
    extras_require={
        'dev': [
            'nbstripout==0.3.9',
            'pytest==6.0.2',
            'pytest-flake8==1.0.6',
            'pytest-isort==1.2.0',
        ],
        'data_vis': [
            'numpy==1.18.1',
            'pandas==1.1.3',
            'plotly==4.12.0',
            'seaborn==0.11.0',
        ],
        'train': [
            'PyEEGLab==0.10.0',
            'scikit-learn==0.23.2',
            'tensorflow==2.3.0'
            'tensorboard==2.3.0',
            'tqdm==4.50.2',
        ]
    }
)
