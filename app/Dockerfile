FROM tiangolo/uvicorn-gunicorn
WORKDIR /project
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PYTHONPATH=/project
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]