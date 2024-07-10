# container image
FROM python:3.10

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# create root directory in the container
RUN mkdir /notif_webhook_unifonic

# Set the working directory
WORKDIR /notif_webhook_unifonic

# Copy the current directory contents into the container
ADD . /notif_webhook_unifonic/

# Install system dependencies
RUN apt-get update \
  && apt-get install -y netcat-openbsd gcc nginx \
  && apt-get clean

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Collect static files
#RUN python manage.py collectstatic
#RUN python manage.py makemigrations
#RUN python manage.py migrate

# Start gunicorn
CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "notif_webhook_unifonic.wsgi:application"]