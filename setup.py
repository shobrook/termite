import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

if sys.version_info[:3] < (3, 0, 0):
    print("Requires Python 3 to run.")
    sys.exit(1)

setup(
    name="termite-ai",
    version="1.0.1",
    description="Generate terminal UIs from simple text prompts",
    url="https://github.com/shobrook/termite",
    author="shobrook",
    author_email="shobrookj@gmail.com",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Natural Language :: English",
        "Programming Language :: Python",
    ],
    keywords="openai claude cli commandline tui terminal generative-ui",
    include_package_data=True,
    packages=find_packages(),
    entry_points={"console_scripts": ["termite = termite.__main__:main"]},
    install_requires=["openai", "anthropic", "ollama", "urwid", "rich", "textual"],
    requires=["openai", "anthropic", "ollama", "urwid", "rich", "textual"],
    python_requires=">=3",
    license="Apache License",
)
