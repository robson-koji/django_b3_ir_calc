FROM ubuntu:18.04
RUN apt-get update && apt-get install \
  -y --no-install-recommends python3 python3-virtualenv

RUN apt-get -y install -qq --force-yes vim

# /root/.bashrc
RUN touch /root/.bashrc \
 && echo 'set -o vi' >> /root/.bashrc

# Cronjob
RUN apt-get -y install -qq --force-yes cron
COPY tasks/cronjobs /etc/cron.d/cronjobs
RUN chmod 0644 /etc/cron.d/cronjobs
RUN crontab /etc/cron.d/cronjobs
RUN touch /var/log/cron.log
CMD ["crond", "-f"]

#CMD cron && tail -f /var/log/cron.log


# To use in Django settings.py
ENV IS_DOCKER=1
ENV VIRTUAL_ENV=/opt/venv
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
