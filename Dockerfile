FROM python:3.9.8

RUN apt update

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

COPY . /app
WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["python", "app.py"]