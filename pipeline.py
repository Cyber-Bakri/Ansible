from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="django-hello",
    version="0.1.0",
    description="Simple Django application for CI/CD testing",
    author="U.S. Bank",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=requirements,
    include_package_data=True,
)

