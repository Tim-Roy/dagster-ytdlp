from setuptools import find_packages, setup

setup(
    name="dag_ytdlp",
    packages=find_packages(),
    install_requires=[
        "dagster~=1.7.12",
        "dagster-docker~=0.23.12",
        "dagster-postgres~=0.23.12",
        "pendulum<3.0",
        "psycopg2-binary~=2.9.9",
        "pyyaml~=6.0.1",
        "SQLAlchemy~=2.0.28",
        "yt-dlp~=2024.5.27",
    ],
    extras_require={
        "dev": ["ruff~=0.4.8", "ipykernel~=6.29.3"],
    },
)
