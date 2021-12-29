FROM python:3.6
RUN apt-get update

#COPY ./requirements.txt /tmp/requirements.txt
#WORKDIR /tmp
#RUN pip install -r requirements.txt

COPY . /api  
WORKDIR /api
RUN pip install -r requirements.txt
RUN python -m nltk.downloader punkt

CMD ["gunicorn", "main:app", "-b 0.0.0.0:8000", "-w", "4","-t", "1000", "-k","uvicorn.workers.UvicornWorker"]
