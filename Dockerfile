FROM python:3.8

WORKDIR /project
RUN mkdir logs
RUN python -m pip install --upgrade pip

COPY requirements.txt .
RUN  pip install -r requirements.txt

COPY *.py ./
COPY server server
COPY rate_limiting rate_limiting


CMD gunicorn run:start_gunicorn --worker-class aiohttp.worker.GunicornWebWorker --log-level critical --bind 0.0.0.0:8000
#CMD ["python", "-u", "run.py"]
