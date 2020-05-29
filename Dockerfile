#FROM django


FROM ubuntu:18.04
RUN apt-get update && apt-get install \
  -y --no-install-recommends python3 python3-virtualenv

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

ADD . /django_b3_ir_calc

WORKDIR /django_b3_ir_calc

RUN pip install -r requirements.txt


EXPOSE 8000
CMD [ "python", "./manage.py",  "runserver", "0.0.0.0:8000" ]
