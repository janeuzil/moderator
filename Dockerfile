FROM python:2-alpine
EXPOSE 8080

# Install basic utilities
RUN apk add -U ca-certificates --update --no-cache \
  && rm -rf /var/cache/apk/* \
  && pip install --no-cache-dir \
          setuptools \
          wheel

COPY requirements.txt /app/

RUN pip install -r /app/requirements.txt

WORKDIR /app
ADD moderator/ /app/

CMD [ "python", "./moderator.py", "8080" ]
