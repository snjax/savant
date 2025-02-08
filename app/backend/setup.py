from setuptools import setup, find_packages

setup(
    name="app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask==3.0.2',
        'flask-login==0.6.3',
        'google-auth==2.27.0',
        'google-auth-oauthlib==1.2.0',
        'docker==7.0.0',
        'python-dotenv==1.0.1',
        'gunicorn==21.2.0',
        'pymongo==4.6.2',
    ],
) 
