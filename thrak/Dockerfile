FROM daocloud.io/python:2.7

WORKDIR /thrak

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY thrak/ /thrak/

EXPOSE 5000
CMD ["python", "/thrak/api.py"]
