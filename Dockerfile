FROM python:3.11.8-bullseye
WORKDIR /app
COPY . /app
RUN pip3 install .
ENTRYPOINT ["depcleaner"]