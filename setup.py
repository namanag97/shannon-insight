"""Setup script for Shannon Insight"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = ""
readme_path = this_directory / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="shannon-insight",
    version="0.1.0",
    author="Naman Agarwal",
    author_email="",  # Add your email if you want
    description="Multi-signal codebase quality analyzer using mathematical primitives",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/shannon-insight",  # Update with actual repo
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/shannon-insight/issues",
        "Documentation": "https://github.com/yourusername/shannon-insight#readme",
        "Source Code": "https://github.com/yourusername/shannon-insight",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scikit-learn>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "shannon-insight=shannon_insight.cli:main",
        ],
    },
    keywords="code-quality static-analysis codebase-analysis metrics entropy mathematics",
)
