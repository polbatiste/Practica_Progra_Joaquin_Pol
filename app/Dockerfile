FROM tiangolo/uvicorn-gunicorn
WORKDIR /project
COPY requirements.txt /project
RUN pip install -r requirements.txt
COPY . /project
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]