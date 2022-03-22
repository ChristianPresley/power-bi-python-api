FROM python:3.9.7

RUN mkdir staging
COPY . /staging
WORKDIR /staging

CMD ["pip install -r", "requirements.txt"]
