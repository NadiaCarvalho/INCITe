setup(
    name="realpython-reader",
    version="1.0.0",
    description="Read the latest Real Python tutorials",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/realpython/reader",
    author="Real Python",
    author_email="office@realpython.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["interface", "generation", "representation"],
    include_package_data=True,
    install_requires=[
        "music21-5.7.2", "numpy", "scipy", "sklearn", "vmo", "Pillow", "pyqt5", "pyqtspinner"
    ],
    entry_points={"console_scripts": ["realpython=application.__main__:main"]},
)
