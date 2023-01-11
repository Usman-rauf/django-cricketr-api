#pull official base image
FROM python:3.11.1-alpine
# set work directory
WORKDIR /usr/src/app
# set environment variables
RUN cd /usr/src/
RUN python3 -m venv venv
RUN source venv/bin/activate
RUN  cd /usr/src/app
# install dependencies
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt
COPY . /usr/src/app/
# copy project
EXPOSE 8000
# run entrypoint.sh
CMD ["python", "manage.py" ,"runserver" ,"0.0.0.0:3000"]