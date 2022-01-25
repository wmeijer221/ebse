FROM python:3.9

WORKDIR /app/

RUN apt update && apt install screen --yes
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
ENV PATH /root/.local/bin:$PATH

COPY poetry.lock .
COPY pyproject.toml .
RUN poetry install

COPY apache.db .
COPY main.py .
COPY src ./src

CMD ["poetry", "run", "python", "main.py"]
