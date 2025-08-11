#!/usr/bin/env python3
"""
Setup script for Eve Online Crash Monitor
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
def read_requirements():
    """Read requirements.txt and return list of dependencies"""
    requirements: list[str] = []
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    requirements.append(line)
    except FileNotFoundError:
        # Fallback requirements if file doesn't exist
        requirements = [
            "psutil>=5.9.0",
            'pywin32>=306; sys_platform == "win32"'
        ]
    return requirements

setup(
    name="eve-crash-monitor",
    version="1.1.0",
    description="Professional monitoring solution for Eve Online crashes and logs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Eve Crash Monitor Team",
    author_email="",  # Add your email if you want
    url="https://github.com/yourusername/eve-crash-monitor",  # Update with your repo
    license="MIT",
    
    # Package configuration
    packages=find_packages(),
    package_dir={'': 'python'},  # Python files are in the python/ directory
    py_modules=[
        'eve_crash_monitor',
        'crash_monitor_gui', 
        'enhanced_crash_monitor',
        'eveloglite_client',
        'run_monitor_auto',
        'test_installation'
    ],
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Package data
    package_data={
        '': [
            'config/*.json',
            'scripts/*.bat',
            'scripts/*.ps1',
            'docs/*.md',
            'requirements.txt'
        ]
    },
    include_package_data=True,
    
    # Entry points for command-line scripts
    entry_points={
        'console_scripts': [
            'eve-crash-monitor=eve_crash_monitor:main',
            'eve-crash-gui=crash_monitor_gui:main',
            'eve-monitor-auto=run_monitor_auto:main',
        ],
    },
    
    # Classifiers for PyPI
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Games/Entertainment",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
    ],
    
    # Keywords for PyPI search
    keywords="eve online crash monitor gaming windows logs",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/yourusername/eve-crash-monitor/issues",
        "Source": "https://github.com/yourusername/eve-crash-monitor",
        "Documentation": "https://github.com/yourusername/eve-crash-monitor#readme",
    },
    
    # Additional metadata
    zip_safe=False,
)
