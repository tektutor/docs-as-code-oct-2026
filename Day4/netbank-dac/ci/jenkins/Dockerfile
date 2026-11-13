# Jenkins controller with everything the NetBank pipeline needs:
# Python 3, PlantUML, Graphviz, the WeasyPrint libraries, and IBM Plex fonts.
FROM jenkins/jenkins:lts-jdk17
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-venv python3-pip plantuml graphviz curl \
      libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b fonts-ibm-plex \
 && rm -rf /var/lib/apt/lists/*
USER jenkins
# The repository is mounted from your computer and owned by another user.
RUN git config --global --add safe.directory '*'
RUN jenkins-plugin-cli --plugins workflow-aggregator git junit timestamper credentials-binding
