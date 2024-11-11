#FROM ubuntu:23.04 as builder
#
#COPY patch/sources.list /etc/apt/sources.list
#RUN export DEBIAN_FRONTEND=noninteractive \
#    && apt-get update -qq \
#    && apt-get upgrade \
#      --yes -qq --no-install-recommends \
#    && apt-get install \
#      --yes -qq --no-install-recommends \
#      build-essential \
#      ca-certificates \
#      libldap-dev \
#      libpq-dev \
#      libsasl2-dev \
#      libssl-dev \
#      libxml2-dev \
#      libxmlsec1 \
#      libxmlsec1-dev \
#      libxmlsec1-openssl \
#      libxslt-dev \
#      pkg-config \
#      python3-dev \
#      python3-pip \
#      python3-venv \
#    && python3 -m venv /opt/netbox/venv \
#    && /opt/netbox/venv/bin/python3 -m pip install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com --upgrade \
#      pip \
#      setuptools \
#      wheel
#
#COPY requirements.txt requirements-container.txt /
#RUN \
#    # We compile 'psycopg' in the build process
#    sed -i -e '/psycopg/d' /requirements.txt && \
#    # Gunicorn is not needed because we use Nginx Unit
#    # sed -i -e '/gunicorn/d' /requirements.txt && \
#    # We need 'social-auth-core[all]' in the Docker image. But if we put it in our own requirements-container.txt
#    # we have potential version conflicts and the build will fail.
#    # That's why we just replace it in the original requirements.txt.
#    sed -i -e 's/social-auth-core\[openidconnect\]/social-auth-core\[all\]/g' /requirements.txt && \
#    /opt/netbox/venv/bin/pip install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com\
#      -r /requirements.txt \
#      -r /requirements-container.txt
#
####
## Main stage
####
#
#FROM ubuntu:23.04 as main
#
#COPY patch/sources.list /etc/apt/sources.list
#RUN export DEBIAN_FRONTEND=noninteractive \
#    && apt-get update -qq \
#    && apt-get upgrade \
#      --yes -qq --no-install-recommends \
#    && apt-get install \
#      --yes -qq --no-install-recommends \
#      bzip2 \
#      ca-certificates \
#      curl \
#      libldap-common \
#      libpq5 \
#      libxmlsec1-openssl \
#      openssh-client \
#      openssl \
#      python3 \
#      python3-distutils \
#      nginx \
#    && rm -rf /var/lib/apt/lists/*
#
#COPY --from=builder /opt/netbox/venv /opt/netbox/venv
#
## Copy netbox source code
#COPY netbox /opt/netbox/
## Copy the modified 'requirements*.txt' files, to have the files actually used during installation
#COPY --from=builder /requirements.txt /requirements-container.txt /opt/netbox/

FROM 192.168.6.99/devops/netbox:base-1.0

## Copy netbox source code
COPY netbox /opt/netbox/
## Copy the modified 'requirements*.txt' files, to have the files actually used during installation
COPY /requirements.txt /requirements-container.txt /opt/netbox/
COPY docker/configuration.docker.py /opt/netbox/netbox/configuration.py
COPY docker/ldap_config.docker.py /opt/netbox/netbox/ldap_config.py
COPY docker/housekeeping.sh /opt/netbox/housekeeping.sh
COPY configuration/ /etc/netbox/config/
COPY patch/export.py /opt/netbox/venv/lib/python3.11/site-packages/django_tables2/export/export.py

WORKDIR /opt/netbox

# Must set permissions for '/opt/netbox/netbox/media' directory
# to g+w so that pictures can be uploaded to netbox.
RUN mkdir -p static \
      && chown -R root:root media reports scripts \
      && chmod -R g+w media reports scripts \
      # && cd /opt/netbox/ && SECRET_KEY="dummyKeyWithMinimumLength-------------------------" /opt/netbox/venv/bin/python -m mkdocs build \
          # --config-file /opt/netbox/mkdocs.yml --site-dir /opt/netbox/netbox/project-static/docs/ \
      && SECRET_KEY="dummyKeyWithMinimumLength-------------------------" /opt/netbox/venv/bin/python /opt/netbox/manage.py collectstatic --no-input

ENV LANG=C.utf8 PATH=/opt/netbox/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    GUNICORN_WORKER=8 \
    GUNICORN_THREAD=4

EXPOSE 80

CMD nginx -g 'daemon on;'; \
    gunicorn --workers ${GUNICORN_WORKER} --threads ${GUNICORN_THREAD} \
    # --capture-output --enable-stdio-inheritance --timeout 90 --log-level debug netbox.wsgi:application
    --capture-output --enable-stdio-inheritance --timeout 90 netbox.wsgi:application
    #&& exec nginx -g 'daemon off;'
