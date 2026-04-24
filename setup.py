from setuptools import setup, find_packages

setup(
    name="bill-ingestion",
    version="0.1.0",
    description="Automate electricity bill ingestion, processing, and organization",
    author="Mathieu Buisson",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "playwright",
        "pymupdf4llm",
        "google-api-python-client",
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "python-dotenv",
        "requests",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "mypy",
            "bandit",
        ],
    },
    python_requires=">=3.13",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
    ],
)