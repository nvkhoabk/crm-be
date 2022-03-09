FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /src
WORKDIR /src
ADD . /src/
RUN apt-get update
RUN apt-get install -y git
RUN git init
RUN apt-get install -y gcc python3-dev
RUN apt-get install -y libxml2-dev libxslt1-dev build-essential python3-lxml zlib1g-dev
RUN apt-get install -y default-mysql-client default-libmysqlclient-dev
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN rm get-pip.py
RUN pip install -r requirements.txt