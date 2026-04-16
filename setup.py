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
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "python-dotenv",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)