from setuptools import setup, find_packages
from pathlib import Path

readme_path = Path(__file__).parent / 'README.rst'

with open(readme_path, "r", encoding='utf-8-sig') as f:
    long_desc = f.read()


setup(
    name='kweather-cord',
    version='0.0.4',
    author='Gooraeng',
    author_email='birdyoon1998@gmail.com',
    url='https://github.com/Gooraeng/KweatherDiscord',
    description='Nice Embed Template for Korean Weather for Discord Bot',
    long_description=long_desc,
    long_description_content_type='text/x-rst',
    keywords=['koreaweather', 'kweather', '공공데이터포털', '기상청', 'discord', 'discord.py'],
    packages=find_packages(),
    package_data={
        'kweathercord' : ['area/*', 'asset/img/*'],
    },
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=[
        "discord.py>=2.4.0",
        "pydantic",
        "rapidfuzz",
    ],
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)