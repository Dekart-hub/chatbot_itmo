import re
import os
import requests
import fitz  
from bs4 import BeautifulSoup
from config import PROGRAMS, PLANS_DIR, DATA_DIR, PDF_DOWNLOAD_LINKS

def download_pdfs():
    """Скачивает PDF-файлы по прямым ссылкам."""
    print("--- Начало скачивания PDF ---")
    PLANS_DIR.mkdir(exist_ok=True)
    for filename, url in PDF_DOWNLOAD_LINKS.items():
        try:
            output_path = PLANS_DIR / filename
            if output_path.exists():
                print(f"Файл {filename} уже существует, пропускаю.")
                continue
            
            print(f"Скачиваю {filename} из {url}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"Успешно сохранено в {output_path}")

        except requests.RequestException as e:
            print(f"Ошибка при скачивании {filename}: {e}")
            print("Возможно, ссылка устарела. Попробуйте скачать PDF вручную в папку study_plans.")
            print("Для надежного скачивания рекомендуется использовать Selenium-парсер.")

def parse_websites():
    """Парсит текстовое содержимое со страниц программ."""
    print("\n--- Начало парсинга сайтов ---")
    DATA_DIR.mkdir(exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    for key, details in PROGRAMS.items():
        try:
            print(f"Парсинг страницы: {details['url']}")
            response = requests.get(details['url'], headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            for tag in soup(["script", "style", "header", "footer"]):
                tag.decompose()
            
            text = soup.get_text(separator="\n", strip=True)
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            details['page_txt'].write_text(text, encoding='utf-8')
            print(f"Текст со страницы сохранен в {details['page_txt']}")
        except requests.RequestException as e:
            print(f"Не удалось получить доступ к {details['url']}: {e}")

def extract_text_from_pdfs():
    """Извлекает и очищает текст из скачанных PDF."""
    print("\n--- Начало извлечения текста из PDF ---")
    pdf_to_program_map = {
        "10033-abit.pdf": "ai",
        "10130-abit.pdf": "ai_product"
    }

    for pdf_name, prog_key in pdf_to_program_map.items():
        pdf_path = PLANS_DIR / pdf_name
        if not pdf_path.exists():
            print(f"PDF файл не найден: {pdf_path}. Пропускаю.")
            continue
        
        try:
            print(f"Обработка {pdf_path}...")
            doc = fitz.open(pdf_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text("text")
            doc.close()

            text = re.sub(r"(\w)-\n(\w)", r"\1\2", full_text) 
            text = re.sub(r'\n{3,}', '\n\n', text).strip()
            
            output_path = PROGRAMS[prog_key]['plan_txt']
            output_path.write_text(text, encoding='utf-8')
            print(f"Текст учебного плана сохранен в {output_path}")

        except Exception as e:
            print(f"Ошибка при обработке файла {pdf_path}: {e}")

if __name__ == "__main__":
    download_pdfs()
    parse_websites()
    extract_text_from_pdfs()
    print("\n--- Подготовка данных завершена! ---")