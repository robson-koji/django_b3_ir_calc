Configuração e setup de testes funcinando para criar e subir um container.

```
​Dockerfile
==========
FROM ubuntu:18.04
RUN apt-get update && apt-get install \
  -y --no-install-recommends python3 python3-virtualenv

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

ADD . /project_folder

WORKDIR /project_folder

RUN pip install -r requirements.txt

EXPOSE 8000
CMD [ "python", "./manage.py",  "runserver", "0.0.0.0:8000" ]


Docker build
============
docker build --tag build_name .


Docker run
==========
docker run -t -d --publish 8000:8000 build_name

```



**Listar, parar, excluir**
* docker ps -a
* docker stop CONTAINER_ID
* docker rm CONTAINER_ID

**Entrar**
* docker exec -it CONTAINER_ID bash

**Transferir imagens**
* docker images
* docker save -o <path for generated tar file> <image name>
it is better to use repo:tag as the image reference rather than image id. If you use image id, the loaded image will not retain the tag (and you will have to do another step to tag the image).

* docker load -i <path to image tar file>


**Log**

* docker logs container_id  --follow

Começar a conectar diferentes containers (BV, Nginx, uwsgi, MySQL, Solr, etc):
https://docs.docker.com/engine/tutorials/networkingcontainers/





**Váriaveis de ambiente**
* Utilizar variável de ambiente para configurar o settings.py/local_settings.py se aplicação está rodando no docker ou não.
* IS_DOCKER = os.environ.get('IS_DOCKER', 0)​
* Ver do Dockerfile e no docker-compose.yml variáveis de ambiente (IS_DOCKER, PYTHONPATH, etc)


**gitlab**
* https://www.stavros.io/posts/how-deploy-django-docker/


**local_settings.py**
* http://michal.karzynski.pl/blog/2015/04/19/packaging-django-applications-as-docker-container-images/
* https://stackoverflow.com/a/27753725
* IS_DOCKER (varia conforme o ambiente, para poder rodar sem o docker)


**hot code reloading**
* https://stackoverflow.com/a/41453123


**Django migrate - Migrar direto no container**
* docker-compose exec web python manage.py migrate



**Passos**
* Dockerfile
* docker-compose.yml
* docker-compose up



**Para acessar o debuger no container**

Incluir normalmente no código: **import pdb; pdb.set_trace()**

Claro que o volume precisa estar montado para hot code reloading, e somente em ambiente de dev.

* docker ps -a - pegar o id do container
* docker attach **id_do_container** - para acessar o pdb





Para fazer o deploy.
Fazer o docker save -o
Fazer o ssh do arquivo gerado
Fazer o docker load -i arquivo.tar
Copiar o Dockerfile e o docker compose.yml
Subir com o comando docker-compose up

Pendencia
  - Ver se estao mantendo os volumes
  - crontab foi comentado. Tentar fazer funcionar
  - Integrar as recomendacoes da 11



sf@vmi232710:/var/tmp$ ls -ltr
total 569828
-rw------- 1 sf   sf   583483904 Jul  9 22:17 django_b3_ir_calc_web_static_files.tar
drwxr-xr-x 4 root root      4096 Jul  9 22:40 django_b3_ir_calc
-rw-rw-r-- 1 sf   sf        1077 Jul  9 22:46 Dockerfile
-rw-rw-r-- 1 sf   sf         801 Jul  9 23:41 docker-compose.yml
