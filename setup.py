from setuptools import setup, find_packages

setup(
    name="py-deepseek-api",
    version="1.0.1",
    author="robbinhust",
    description="Unoffical DeepSeek API for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/robbinhust/py-deepseek-api",
    packages=find_packages(),
    package_data={
        "deepseek.utils": ["sign.wasm"],
    },
    include_package_data=True,
    install_requires=[
        "requests>=2.32.3",
        "safe-dict>=1.0.3",
        "wasmtime>=29.0.0",
        "pycryptodome>=3.21.0",

    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
