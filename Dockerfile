# Use the Python3.7.2 image
FROM python:3.9-slim

# Set the working directory to /flask_app
WORKDIR /flask_app

# Copy the current directory contents into the container at /flask_app 
ADD . /flask_app

# Install the dependencies
RUN pip install -r requirements.txt

EXPOSE 5000/tcp

ENV APP_NAME="Poker"

# run the command to start uWSGI
CMD gunicorn --bind 0.0.0.0:5000 wsgi:app
