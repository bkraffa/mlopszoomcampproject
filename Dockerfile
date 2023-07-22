FROM python:3.10-slim
RUN pip install -U pip
RUN pip install pipenv
RUN pip install awscli

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_REGION=us-east-2

ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
ENV AWS_REGION=us-east-2

WORKDIR /app

COPY ["Pipfile" , "Pipfile.lock" , "./" ]

RUN pipenv install --system --deploy

COPY [ "predict.py", "predict.py" ]
COPY [ "models/preprocessor.b", "models/preprocessor.b" ]

ENTRYPOINT [ "python", "predict.py" ]