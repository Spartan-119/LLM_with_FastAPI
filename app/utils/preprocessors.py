import httpx
from bs4 import BeautifulSoup


def extract_text_from_url(url: str) -> str:
    response = httpx.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return " ".join(p.get_text() for p in soup.find_all("p"))


# Add more preprocessor functions here
PREPROCESSORS = {
    "extract_text_from_url": extract_text_from_url,
    # Add more preprocessors as needed
}
