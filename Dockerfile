FROM django

ADD . /django_b3_ir_calc

WORKDIR /django_b3_ir_calc

RUN pip install -r requirements.txt

CMD [ "python", "./manage.py runserver 0.0.0.0:8000" ]
