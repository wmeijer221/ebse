FROM python:3.9-bullseye

WORKDIR /app/scripts

COPY ./scripts .

RUN pip install -r requirements.txt

# Install sonar-scanner
RUN wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.6.2.2472-linux.zip
RUN unzip sonar-scanner-cli-4.6.2.2472-linux.zip
ENV PATH="${PATH}:/app/sonar-scanner-4.6.2.2472-linux/bin"
