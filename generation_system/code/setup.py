setup(
    name="My Musical Suggestor",
    version="1.0.0",
    description="Create Suggestions for continuating a piece of music.",
    long_description='../README',
    long_description_content_type="text/markdown",
    url="https://github.com/NadiaCarvalho/Dissertation",
    author="Nádia Carvalho",
    author_email="ei12047@fe.up.pt; nadiacarvalho118@gmail.com",
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
