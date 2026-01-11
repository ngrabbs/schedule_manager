from setuptools import setup, find_packages

setup(
    name="schedule-manager",
    version="0.1.0",
    description="AI-powered schedule manager with ntfy.sh notifications",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
        "pyyaml>=6.0",
        "apscheduler>=3.10.4",
        "mcp>=0.9.0",
    ],
    entry_points={
        'console_scripts': [
            'schedule-daemon=schedule_manager.daemon:main',
            'schedule-mcp=schedule_manager.mcp_server:main',
        ],
    },
    python_requires='>=3.8',
)
