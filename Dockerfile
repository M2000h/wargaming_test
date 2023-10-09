FROM python:3.9.8

RUN apt update

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

COPY test-requirements.txt /app/test-requirements.txt
RUN pip3 install -r /app/test-requirements.txt

COPY . /app
WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app"

# TODO: тесты выполняются здесь до возможности разместить их в цепочке ci/cd
RUN pytest tests

CMD ["python", "app.py"]