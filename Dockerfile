FROM python:3.6-alpine3.13

ENV PYTHONUNBUFFERED 1
ENV APP_ROOT /code
 
RUN mkdir ${APP_ROOT}
WORKDIR ${APP_ROOT}
ADD . ${APP_ROOT}

# Install postgres client
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

ADD requirements.txt /code/
RUN python -m pip install --upgrade pip
RUN pip install -r /code/requirements.txt

COPY . ${APP_ROOT}