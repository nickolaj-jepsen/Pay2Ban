# Copyright 2013 Thatcher Peskens
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM ubuntu:14.04

MAINTAINER Dockerfiles

RUN apt-get update
RUN apt-get install -y build-essential git
RUN apt-get install -y python3 python3-dev python3-pip python3-setuptools
RUN apt-get install -y nginx supervisor

# install uwsgi now because it takes a little while
RUN pip3 install uwsgi

# install nginx
RUN apt-get install -y software-properties-common python-software-properties
RUN add-apt-repository -y ppa:nginx/stable
RUN apt-get install -y libpq-dev python-dev libssl-dev libffi-dev

# install our code
ADD . /home/docker/code/

# setup all the configfiles
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/sites-enabled/default
RUN ln -s /home/docker/code/nginx-app.conf /etc/nginx/sites-enabled/
RUN ln -s /home/docker/code/supervisor-app.conf /etc/supervisor/conf.d/

# run pip install
RUN pip3 install -r /home/docker/code/requirements.txt

# Make log location for scheduler
RUN mkdir /logs 

VOLUME /home/docker/code/app

EXPOSE 80
CMD ["supervisord", "-n"]
