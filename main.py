import psycopg2
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, Path


def db_connect():
    conn = psycopg2.connect(
        database="foodbit",
        user="postgres",
        password="postgres",
        host="127.0.0.1",
        port="5432",
    )
    return conn

app = FastAPI()

@app.post("/food/{item_name}")
async def read_item(item_name):
    url = f"https://en.wikipedia.org/wiki/{item_name}"
    r = requests.get(url)
    htmlContent = r.content
    soup = BeautifulSoup(htmlContent, "html.parser")
    data = soup.find_all("tr")
    col = ["Course", "Region or state", "Main ingredients"]
    details = []
    for i in data:
        if i.th:
            if i.find("th").get_text() in col:
                details.append(i.find("td").get_text())
    # import pdb; pdb.set_trace();
    intro = soup.find(class_="infobox hrecipe adr").findNext('p').text
    # print(intro)
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO food (NAME,COURSE,REGION,MAININGREDIENTS,INTRODUCTION) VALUES ('{0}','{1}','{2}','{3}','{4}');".format(item_name, details[0],details[1],details[2], intro))
    conn.commit()
    conn.close()
    return "Success"

@app.get("/foodlist/")
async def list_item():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT  name FROM food")
    item = cur.fetchall()
    conn.commit()
    conn.close()
    return item  

@app.get("/food_details/{item_name}")
async def item_details(item_name):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute(f"SELECT  * FROM food WHERE name = '{item_name}'")
    item = list(cur.fetchone())
    cur.execute("SELECT Column_name FROM   Information_schema.columns WHERE  Table_name like 'food'")
    column = cur.fetchall()
    columns=list(map(lambda i:i[0], column))
    item = item[-1:] + item[:-1]
    result = dict(zip(columns,item))
    conn.commit()
    conn.close()
    return result
     

