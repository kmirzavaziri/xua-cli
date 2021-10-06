import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name='xua',
    version='1.0-β',
    scripts=['./scripts/xua'],
    author='Kamyar Mirzavaziri',
    author_email='kmirzavaziri@gmail.com',
    description='Xua: A PHP Code Generator',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/kmirzavaziri/xua-cli',
    project_urls = {
        "Docs": "http://xuarizmi.ir/docs/"
    },
    license='MIT',
    packages=['xua'],
    install_requires=['weasyprint'],
)