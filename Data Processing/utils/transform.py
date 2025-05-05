import re

def transform(data):
    transformed_data = []
    for item in data:
        title = item["title"]
        
        # Menghapus karakter non-angka dari harga
        price = re.sub(r"[^\d]", "", item["price"])
        price = int(price) if price else 0  # Jika kosong, jadikan 0
        
        transformed_data.append({"title": title, "price": price})
    
    return transformed_data
