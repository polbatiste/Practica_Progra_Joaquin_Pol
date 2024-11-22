FROM tiangolo/uvicorn-gunicorn
WORKDIR /project
COPY requirements.txt /project
RUN pip install -r requirements.txt
COPY . /project
WORKDIR /project/app
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]