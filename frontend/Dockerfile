FROM python:3.12-slim

WORKDIR /app/frontend

COPY frontend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt || pip install --no-cache-dir django htmx-django requests

COPY frontend ./

EXPOSE 3000

CMD ["python", "manage.py", "runserver", "0.0.0.0:3000"]
