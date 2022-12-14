FROM python:3
LABEL maintainer sturm@uni-trier.de
RUN apt-get update && apt-get install -y
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR dashboard
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py ./
EXPOSE 4343
CMD [ "python", "dashboard_coreef.py" ]

