import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="3tier-cdk-python",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="localhost",

    package_dir={"": "3tier-cdk-python"},
    packages=setuptools.find_packages(where="3tier-cdk-python"),

    install_requires=[
        "aws-cdk.core==1.96.0",
    ],

    python_requires=">=3.6",
)
