from setuptools import setup

setup(
    name="depcleaner",
    author="William Turner",
    license="All Rights Reserved",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
    author_email="will.turner@sure.com",
    version="0.0.1",
    package_dir={"": "src"},
    # ackage_data={"": ["assets/logo.txt"]},
    include_package_data=True,
    #py_modules=["depcleaner",],
    install_requires=['click', 'boto3'],
    entry_points={
        "console_scripts": [
            "depcleaner = depcleaner:cli",
        ],
    },
)
