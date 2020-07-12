#FROM ubuntu:18.04
#RUN apt-get update && apt-get install \
# -y --no-install-recommends python3 python3-virtualenv

FROM python:3

RUN apt-get update && apt-get install \
  -y --no-install-recommends vim git python3-virtualenv

# Para instalar o pdftotext no Python3
# https://github.com/jalan/pdftotext
#RUN apt-get -y install -qq --force-yes build-essential libpoppler-cpp-dev pkg-config python3-dev
RUN apt-get -y install build-essential libpoppler-cpp-dev pkg-config python3-dev

#RUN apt-get -y install -qq --force-yes vim

# /root/.bashrc
RUN touch /root/.bashrc \
 && echo 'set -o vi' >> /root/.bashrc



# Cronjob

# Add crontab file in the cron directory
ADD tasks/cronjobs /etc/cron.d/syncdb-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/syncdb-cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

#Install Cron
RUN apt-get update
RUN apt-get -y install cron


# Run the command on container startup
# !!! Se deixa com essa linha, sobe um container com o cron funcionando.
# Tentar habilitar o cron do docker-compose.yml
# Mesmo aqui, tentando acessar o sqlite, nao monta o volume......

### !!!!!!!!!! - 12/Jul/2020 - Parando aqui. 
# CMD cron && tail -f /var/log/cron.log









# To use in Django settings.py
ENV IS_DOCKER=1
ENV VIRTUAL_ENV=/opt/venv
RUN pip install virtualenv
RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

# Workdir
ARG workdir='/django_b3_ir_calc'
ADD . ${workdir}
WORKDIR ${workdir}
ENV PYTHONPATH=${workdir}


# Montanto volume no docker-compose.yml
#VOLUME /django_b3_ir_calc/django_b3_ir_calc/local_settings.py

# Expondo no docker-compose.yml
#EXPOSE 8000
#CMD [ "python", "./manage.py",  "runserver", "0.0.0.0:8000" ]
