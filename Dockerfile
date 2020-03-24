FROM python:3.8

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./convert_image.py ./
COPY ./main.py ./

EXPOSE 8080
CMD ["python", "main.py"]
