from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader
from bs4 import BeautifulSoup
import requests
import base64

class FreshserviceLoader(BaseLoader):
    def __init__(self, api_key: str, article_id: int, omit_metadata: bool = False) -> None:
        self.api_key = api_key
        self.article_id = article_id
        self.omit_metadata = omit_metadata
        self.base_url = "https://charusat.freshservice.com/api/v2/solutions/articles/"

        self.auth_header = {
            "Authorization": "Basic " + base64.b64encode(f"{self.api_key}:X".encode()).decode()
        }

    def _extract_text(self, html_content: str) -> str:
        if not html_content:
            return ""
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator=" ").strip()

    def lazy_load(self):
        response = requests.get(
            f"{self.base_url}{self.article_id}",
            headers=self.auth_header,
        )

        if response.status_code != 200:
            raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

        data = response.json()
        article = data.get("article", {})
        article_content = article.get("description", "")
        clean_content = self._extract_text(article_content)

        if self.omit_metadata:
            return [Document(page_content=clean_content)]
        else:
            metadata = {
                "title": article.get("title"),
                "status": article.get("status"),
                "created_at": article.get("created_at"),
                "updated_at": article.get("updated_at"),
            }
            return [Document(page_content=clean_content, metadata=metadata)]


api_key = "QFN39X1g60Gi9Qo9mbf-"  
article_id = 29000041041        

loader = FreshserviceLoader(api_key, article_id, omit_metadata=False)
documents = loader.lazy_load()

print(documents[0].page_content)
for doc in documents:
    print(doc.metadata)

