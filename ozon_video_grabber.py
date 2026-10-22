import os
import re
import sys
import json
import requests

def get_product_id(url_or_id: str) -> str:
    """Извлекает ID товара из ссылки или строки."""
    match = re.search(r'(\d+)', url_or_id)
    if match:
        return match.group(1)
    raise ValueError("Не удалось определить ID товара.")

def grab_ozon_data(product_input: str, output_dir: str = "ozon_videos"):
    product_id = get_product_id(product_input)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"[*] Сбор отзывов для товара ID: {product_id}")
    
    api_url = f"https://www.ozon.ru/api/composer-api.bx/page/json/v2?url=/product/{product_id}/reviews"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8',
        'Referer': f'https://www.ozon.ru/product/{product_id}/',
    }

    session = requests.Session()
    
    try:
        response = session.get(api_url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[×] Ошибка API: статус {response.status_code}")
            return

        data = response.json()
        json_str = json.dumps(data)
        
        video_urls = set(re.findall(r'https?://[^\s"\']+\.(?:mp4|m3u8)', json_str))
        
        if not video_urls:
            print("[!] Видеоотзывы не найдены.")
            return

        print(f"[+] Найдено уникальных видео: {len(video_urls)}")

        for idx, video_url in enumerate(video_urls, 1):
            ext = "mp4" if ".mp4" in video_url else "m3u8"
            file_name = f"review_{product_id}_{idx}.{ext}"
            file_path = os.path.join(output_dir, file_name)
            
            print(f"[{idx}/{len(video_urls)}] Скачивание...")
            res = session.get(video_url, stream=True, timeout=30)
            if res.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in res.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"[✓] Сохранено: {file_path}")
            else:
                print(f"[×] Ошибка скачивания файла: {res.status_code}")

    except Exception as e:
        print(f"[×] Произошла ошибка: {e}")

if __name__ == "__main__":
    target_input = sys.argv[1] if len(sys.argv) > 1 else input("Введите ссылку или ID товара: ")
    grab_ozon_data(target_input)
