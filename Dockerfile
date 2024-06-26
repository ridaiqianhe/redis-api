FROM python:3.10-slim-bullseye

RUN mkdir /app
RUN mkdir /logs
COPY ./*.txt ./*.py ./*.sh ./*.onnx /app/


RUN cd /app \
    && mkdir logs \
    && python3 -m pip install --upgrade pip \
    && pip3 install --no-cache-dir -r requirements.txt \
    && rm -rf /tmp/* && rm -rf /root/.cache/* \
    && apt-get --allow-releaseinfo-change update && apt install libgl1-mesa-glx libglib2.0-0 -y

WORKDIR /app

CMD ["gunicorn", "-c", "gunicorn.py" , "views:app"]
