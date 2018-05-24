FROM python:3.6

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN git clone https://github.com/delagroove/finale_602 /usr/src/app/final_602

RUN python /usr/src/app/final_602/fill_database.py

EXPOSE 5000

CMD [ "python", "/usr/src/app/final_602/main.py" ]
