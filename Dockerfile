FROM python:3.8

WORKDIR /project
RUN mkdir logs
RUN python -m pip install --upgrade pip
RUN pip install poetry
COPY poetry.lock .
COPY pyproject.toml .
RUN poetry install

COPY *.py ./
COPY exceptions/ exceptions/
COPY middleware/ middleware/
COPY rate_limiting/ rate_limiting/
COPY server/ server/

CMD poetry run gunicorn run:start_gunicorn --worker-class aiohttp.worker.GunicornWebWorker --log-level critical --bind 0.0.0.0:8000
#CMD ["poetry", "run", "python", "-u", "run.py"]
