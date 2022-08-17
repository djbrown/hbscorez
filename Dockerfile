FROM python:3.10-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends default-jre fonts-liberation gsfonts locales \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN echo "de_DE.UTF-8 UTF-8" >> /etc/locale.gen \
    && locale-gen

RUN pip install pipenv==2022.1.8 gunicorn==20.1.0

ENV HOME=/code
RUN mkdir $HOME
WORKDIR $HOME
RUN chown -R 1001 $HOME \
    && chgrp -R 1001 $HOME \
    && chmod -R g+rwx $HOME

USER 1001:1001

COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --deploy
# RUN pipenv install --skip-lock gunicorn==20.1.0

COPY entrypoint.sh .
COPY src/ src/

# USER root
# RUN touch $HOME/hbscorez.log
# RUN chgrp -R 1001 $HOME/hbscorez.log \
#     && chown -R o+rwx $HOME/hbscorez.log
# USER 1001:1001

ENTRYPOINT ["./entrypoint.sh"]
