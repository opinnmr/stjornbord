############################################################
# Dockerfile to run a Django-based web application
# Based on an Ubuntu Image
#
# Based on http://michal.karzynski.pl/blog/2015/04/19/packaging-django-applications-as-docker-container-images/
############################################################

# Set the base image to use to Ubuntu
FROM ubuntu:14.04

# Set the file maintainer (your name - the file's author)
MAINTAINER Bjorn Swift

# Set env variables used in this Dockerfile (add a unique prefix, such as DOCKYARD)
# Local directory with project source
ENV DOCKYARD_SRC=.
# Directory in container for all project files
ENV DOCKYARD_SRVHOME=/srv
# Directory in container for project source files
ENV DOCKYARD_SRVPROJ=/srv/stjornbord

# Update the default application repository sources list
COPY /sources.list /etc/apt/sources.list
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python python-pip python-dev gunicorn

# mr
RUN apt-get install -y git subversion python-libxml2 libxmlsec1 libxmlsec1-dev

# Create application subdirectories
WORKDIR $DOCKYARD_SRVHOME
RUN mkdir media staticlogs
VOLUME ["$DOCKYARD_SRVHOME/media/", "$DOCKYARD_SRVHOME/logs/"]

# Copy application source code to SRCDIR
COPY $DOCKYARD_SRC $DOCKYARD_SRVPROJ

# Install Python dependencies
RUN pip install -r $DOCKYARD_SRVPROJ/requirements.txt
RUN pip install -r $DOCKYARD_SRVPROJ/requirements-sso.txt

# Port to expose
EXPOSE 8000

# Copy entrypoint script into the image
WORKDIR $DOCKYARD_SRVPROJ
COPY ./docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
