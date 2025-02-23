from fastapi import FastAPI
import boto3
import uuid
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from mangum import Mangum


load_dotenv()

app = FastAPI()

dynamodb = boto3.resource('dynamodb')

for table in dynamodb.tables.all():
    print(table.name)
    
table = dynamodb.Table("UrlShortener")


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

class URLItem(BaseModel):
    url: str


@app.post("/shorten")
def shorten_url(item: URLItem):
    short_id = str(uuid.uuid4())[:8]
    table.put_item(
        Item={
            'short_id': short_id,
            'url': item.url
        }
    )
    return {"shortUrl": f"https://your-frontend-url.com/{short_id}"}

@app.get("/{short_id}")
def get_url(short_id: str):
    response = table.get_item(Key={'short_id': short_id})
    if 'Item' not in response:
        return {"error": "URL not found"}
    return {"url": response['Item']['url']}

handler = Mangum(app)