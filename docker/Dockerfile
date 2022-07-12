FROM python:3.9

EXPOSE 8080

WORKDIR /app
COPY . /app
COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY waitress_server.py /
ENTRYPOINT [ "python" ]

CMD ["waitress_server.py" ]