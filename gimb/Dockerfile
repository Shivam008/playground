FROM daocloud.io/python:2.7

WORKDIR /gimb

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY gimb/ /gimb/

CMD ["python", "/gimb/main.py"]
