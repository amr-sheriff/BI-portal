#!/bin/bash
python manage.py makemigrations webhook_receiver
python manage.py migrate