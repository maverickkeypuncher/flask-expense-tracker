FROM python:3.10
WORKDIR /app
COPY app.py /app
COPY requirements.txt /app
COPY templates/ /app/templates/
RUN pip install -r requirements.txt
EXPOSE 5000
#CMD ["python", "app.py"]
