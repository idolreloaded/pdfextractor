import argparse
import re

import fitz

TXT_OUTPUT_PATH = 'extracted_text.txt'

UNWANTED_TEXT: list[str] = []


def extract_text_from_pdf(pdf_path: str) -> str:
    """Функция для извлечения текста из PDF"""

    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text


def decode_text(text: str) -> str:
    """Функция для обработки текста и замены некорректных символов"""

    decoded_chars = []
    for char in text:
        try:
            decoded_char = char.encode('windows-1252').decode('windows-1251')
            decoded_chars.append(decoded_char)
        except UnicodeEncodeError:
            decoded_char = char.encode('utf-8').decode('utf-8')
            decoded_chars.append(decoded_char)
    return ''.join(decoded_chars)


def remove_math_formulas(text: str) -> str:
    """Функция для удаления математических формул из текста"""

    clean_text = re.sub(r'\b[0-9A-Za-z]+\s*=\s*[0-9A-Za-z]+\b', '', text)
    clean_text = re.sub(r'[\(\)\[\]\{\}]+', '', clean_text)
    clean_text = re.sub(r'[a-zA-Z]+\s*[0-9]+\s*', '', clean_text)
    return clean_text


def clean_text(text: str) -> str:
    """Функция для удаления лишних пробелов и строк,
    содержащих только цифры или нули
    """

    clean_text = re.sub(r'^\s*[0-9]+\s*$', '', text, flags=re.MULTILINE)
    clean_text = re.sub(r'^\s*0\s*$', '', clean_text, flags=re.MULTILINE)
    clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)
    clean_text = re.sub(r' {2,}', ' ', clean_text)
    for unwanted_text in UNWANTED_TEXT:
        clean_text = re.sub(fr'{unwanted_text}', '', clean_text)
    return clean_text.strip()


def main(pdf_path: str, txt_output_path: str) -> None:
    """Основная функция. Извлекает, обрабатывает,
    удаляет математические формулы и пробелы. Сохраняет в файл.
    """

    # Шаг 1: Извлечение текста из PDF
    extracted_text = extract_text_from_pdf(pdf_path)

    # Шаг 2: Обработка текста
    decoded_text = decode_text(extracted_text)

    # Шаг 3: Удаление математических формул
    no_formulas_text = remove_math_formulas(decoded_text)

    # Шаг 4: Удаление лишних пробелов и строк
    cleaned_text = clean_text(no_formulas_text)

    # Шаг 5: Сохранение текста в TXT-файл
    with open(txt_output_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog='pdfextractor.py',
                    description='Extracts all the word text from'
                    'PDF and saves it to file',
                    epilog='Takes input and desired output filenames')
    parser.add_argument('input_file', help='Input filename')
    parser.add_argument('output_file', help='Output file name')
    args = parser.parse_args()
    main(args.input_file, args.output_file or TXT_OUTPUT_PATH)
