FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install whitenoise

COPY . .

EXPOSE 8000

CMD ["gunicorn", "endproject.wsgi:application", "--bind", "0.0.0.0:8000"]
