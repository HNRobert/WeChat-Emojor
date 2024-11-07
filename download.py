import logging
import os
import shutil
import subprocess
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import glob

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def find_fav_archive_file():
    # 获取当前用户的用户名和目标文件模式
    home_dir = os.path.expanduser("~")
    search_pattern = os.path.join(
        home_dir,
        "Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/*/Stickers/fav.archive"
    )

    # 查找匹配的文件
    files = glob.glob(search_pattern)
    return files


def copy_and_convert_to_xml(filepath):
    current_dir = os.getcwd()
    filename = os.path.basename(filepath)
    dest_path = os.path.join(current_dir, filename)

    # 复制文件到运行目录
    shutil.copy(filepath, dest_path)

    # 转换文件为 XML 格式
    subprocess.run(['plutil', '-convert', 'xml1', dest_path], check=True)

    return dest_path


def extract_urls_from_xml(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'xml')
    urls = []

    for string_tag in soup.find_all('string'):
        if 'http' in string_tag.text:
            # 将 `&amp;` 替换为 `&`
            url = string_tag.text.replace("&amp;", "&")
            urls.append(url)
            logging.info(f"Extracted URL: {url}")

    return urls


def download_files(urls):
    download_dir = os.path.join(os.getcwd(), 'Download')
    os.makedirs(download_dir, exist_ok=True)

    for index, url in enumerate(urls, start=1):
        try:
            parsed_url = urlparse(url)
            file_ext = os.path.splitext(parsed_url.path)[1].lower()

            # 如果扩展名为空且 URL 包含 `.gif` 关键字，则假设文件为 .gif
            if not file_ext:  # and 'gif' in url.lower()
                file_ext = '.gif'
            elif not file_ext:
                file_ext = '.png'  # 默认设置为 .jpg

            # 生成文件名
            filename = f"image_{index}{file_ext}"

            # 下载文件并保存
            response = requests.get(url, stream=True)
            response.raise_for_status()

            file_path = os.path.join(download_dir, filename)
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

            print(f"Downloaded: {filename}")

        except Exception as e:
            print(f"Failed to download {url}: {e}")


def main():
    files = find_fav_archive_file()
    if not files:
        logging.warning("No fav.archive files found.")
        return
    logging.info(f"Found fav.archive files:\n{files}")

    for filepath in files:
        print(f"Processing file: {filepath}")
        xml_file_path = copy_and_convert_to_xml(filepath)
        urls = extract_urls_from_xml(xml_file_path)
        download_files(urls)


if __name__ == '__main__':
    main()
