import requests
from typing import Iterator, AsyncIterator
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
import base64

class FreshserviceKBLoader(BaseLoader):
   

    def __init__(self, api_url: str, api_key: str) -> None:
        
        self.api_url = api_url
        self.api_key = api_key
        self.auth_header = {
            "Authorization": "Basic " + base64.b64encode(f"{self.api_key}:X".encode()).decode()
        }

    def lazy_load(self) -> Iterator[Document]:
        """Lazy load articles from Freshservice KB one by one."""
        response = requests.get(self.api_url, headers=self.auth_header)
        print("Response Status Code:", response.status_code)
        print("Response Text:", response.text)  
        response.raise_for_status()
        data = response.json()
        print("Parsed JSON:", data)  
        for article in data.get("articles", []):
            yield Document(
                page_content=article.get("description", ""),
                metadata={
                    "id": article.get("id"),
                    "title": article.get("title"),
                    "category": article.get("category_id"),
                    "folder": article.get("folder_id"),
                    "source": self.api_url
                },
            )

    def load(self) -> list[Document]:
        """Load all articles from Freshservice KB at once."""
        return list(self.lazy_load())


api_url = ""
api_key = ""

loader = FreshserviceKBLoader(api_url, api_key)


for doc in loader.lazy_load():
    print(doc)
