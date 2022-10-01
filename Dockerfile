# syntax=docker/dockerfile:1
FROM python:3.10.7-bullseye
# RUN apk add --no-cache python2 g++ make
WORKDIR /app
COPY . .
RUN pip install -r requeriments.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# EXPOSE 3000