FROM python:3.10-buster
WORKDIR /usr/src/backend
COPY requirements.txt /usr/src/backend
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8080