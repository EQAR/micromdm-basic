FROM python:3-alpine

ADD requirements.txt /webhook/

WORKDIR /webhook

RUN pip3 install -r requirements.txt

ADD . /webhook

CMD python3 -m gunicorn -b :8000 'app:create_app()'

