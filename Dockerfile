FROM continuumio/anaconda3

RUN apt-get update \
    && apt-get -y install sudo \
    && apt-get install -y locales \
    && apt-get update \
    && dpkg-reconfigure -f noninteractive locales \
    && locale-gen C.UTF-8 \
    && /usr/sbin/update-locale LANG=C.UTF-8 \
    && echo "en_US.UTF-8" >> /etc/locale.gen \
    && echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
    && locale-gen \
    && apt-get install -y curl unzip \
    && apt-get clean \
    && apt-get autoremove

# Create Application Source code Directory

RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/app/data
RUN mkdir -p /usr/src/app/data/input

# Setting Home directory for containers
WORKDIR /usr/src/app

# Installing python dependencies
COPY requirements.txt /usr/src/app/

RUN apt-get install -y poppler-utils

RUN pip install --no-cache-dir -r requirements.txt
RUN wget --no-check-certificate https://dl.xpdfreader.com/xpdf-tools-linux-4.04.tar.gz
RUN tar -xvf xpdf-tools-linux-4.04.tar.gz && sudo cp xpdf-tools-linux-4.04/bin64/pdftotext /usr/local/bin

# Copy src code to container
COPY . /usr/src/app

RUN chmod -R 777 /usr/src/app/data/input
RUN chmod -R 777 /usr/src/app/data
RUN chmod -R 777 /usr/src/app
RUN chmod -R 777 /usr/src

# Application Environment variables
ENV APP_ENV development
ENV PORT 8777

# Expose Ports
EXPOSE $PORT

## Setting persistence
#VOLUME ['/app-data']

# Running application
#CMD gunicorn -b :$PORT main:app --timeout 30 --reload
ENTRYPOINT ["python"]
CMD ["main.py"]
