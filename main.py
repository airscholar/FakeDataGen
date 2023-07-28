from datetime import date

import faker
import psycopg2
from flask import Flask, jsonify, Response
import json

app = Flask(__name__)
fake = faker.Faker()
def db_connect():
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='postgres',
        host='localhost'
    )

    return conn

def create_table():
    """
    Customer table
    :return:
    """
    conn = db_connect()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS public.customer
        (
            customer_id     SERIAL PRIMARY KEY ,
            first_name      VARCHAR(255) NOT NULL,
            last_name       VARCHAR(255) NOT NULL,
            email           VARCHAR(255) NOT NULL,
            address         VARCHAR(255) NOT NULL,
            phone_number    VARCHAR(255) NOT NULL,
            date_of_birth   DATE NOT NULL,
            date_created    DATE NOT NULL DEFAULT CURRENT_DATE,
            date_updated    DATE NOT NULL DEFAULT CURRENT_DATE
        )
        """
    )
    conn.commit()
    cur.close()
    conn.close()
def populate_table_with_fakes():
    """
    Populate the table with fake data
    :return:
    """
    conn = db_connect()
    cur = conn.cursor()

    customers = []

    for i in range(10, 101):
        customers.append(
            (i,
             fake.first_name(),
             fake.last_name(),
             fake.email(),
             fake.address(),
             fake.phone_number(),
             fake.date_of_birth(minimum_age=18, maximum_age=70)))

    cur.executemany(
        """
        INSERT INTO public.customer
        (customer_id, first_name, last_name, email, address, phone_number, date_of_birth)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        customers
    )

    cur.close()
    conn.commit()
    conn.close()

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat() # serialize date as a string in ISO format
        return super().default(obj)

@app.route('/customers', methods=["GET"])
def customer():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute('SELECT * FROM public.customer')

    customers = cur.fetchall()

    cur.close()
    conn.close()

    column_names = [desc[0] for desc in cur.description]
    customers_list = [dict(zip(column_names, customer)) for customer in customers]

    json_data = json.dumps(customers_list, indent=2, cls=CustomJSONEncoder)
    return Response(json_data, content_type='application/json')

if __name__ == '__main__':
    populate_table_with_fakes()