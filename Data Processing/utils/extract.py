import requests
from bs4 import BeautifulSoup

def extract():
    url = "https://fashion-studio.dicoding.dev/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Contoh mengambil semua produk dalam <div class="product">
        products = []
        for product in soup.find_all("div", class_="product"):
            title = product.find("h2").text.strip() if product.find("h2") else "Unknown"
            price = product.find("span", class_="price").text.strip() if product.find("span", class_="price") else "Unknown"
            products.append({"title": title, "price": price})

        return products
    else:
        raise Exception(f"Failed to retrieve data: {response.status_code}")
