from setuptools import setup, find_packages

setup(
    name="auth-service",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "bcrypt>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
        ],
    },
)