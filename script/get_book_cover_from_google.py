"""
通过谷歌图片搜索获取书籍封面：以「md 文件名 + 书籍」为关键词，
取第一张图片下载为 cover.jpg。输入输出与 get_book_covers 一致，供其作为备选。
"""
import os
import re
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_FOLDER = os.path.join(ROOT_DIR, '..', '读书')
COVER_FILENAME = 'cover.jpg'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
}


def _first_image_url_from_google(keyword):
    """
    用关键词请求谷歌图片搜索页，解析出第一张图片的 URL。
    先尝试从页面内嵌 JSON 中匹配 "ou":"URL"，再尝试常见 img 结构。
    返回 URL 或 None。
    """
    query = urllib.parse.quote(keyword)
    url = f'https://www.google.com/search?q={query}&tbm=isch'
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        r = session.get(url, timeout=15)
        r.raise_for_status()
        text = r.text
    except Exception as e:
        print(f"谷歌图片搜索请求失败: {keyword}, 错误: {str(e)}")
        return None

    # 1) 从内嵌 JSON 中取第一个 "ou":"https://..."（谷歌图片结果常用）
    ou_matches = re.findall(r'"ou"\s*:\s*"(https?://[^"]+)"', text)
    for raw_url in ou_matches:
        unescaped = raw_url.encode().decode('unicode_escape') if '\\u' in raw_url else raw_url
        if unescaped.startswith('http') and 'google.com' not in unescaped and 'gstatic.com' not in unescaped:
            return unescaped

    # 2) 备用：页面上带 data-src 或 src 的图片（可能是缩略图）
    soup = BeautifulSoup(text, 'html.parser')
    for img in soup.find_all('img'):
        src = img.get('data-src') or img.get('src')
        if not src or not src.startswith('http'):
            continue
        if 'google.com' in src or 'gstatic.com' in src:
            continue
        return src

    return None


def _download_image_to_path(image_url, md_file_path):
    """下载 image_url 到 md 所在目录的 cover.jpg，返回 COVER_FILENAME 或 None。"""
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        r = session.get(image_url, timeout=15)
        r.raise_for_status()
        ct = (r.headers.get('Content-Type') or '').lower()
        if 'image' not in ct and 'octet-stream' not in ct:
            print(f"非图片响应: {image_url[:80]}..., Content-Type: {ct}")
            return None
        folder = os.path.dirname(md_file_path)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, COVER_FILENAME)
        with open(path, 'wb') as f:
            f.write(r.content)
        return COVER_FILENAME
    except Exception as e:
        print(f"下载谷歌封面失败: {image_url[:60]}..., 错误: {str(e)}")
        return None


def fetch_and_download_cover_from_google(md_file_path):
    """
    根据 md 文件路径得到书名（文件名去掉扩展名）+「书籍」作为关键词，
    谷歌图片搜索取第一张图，下载到 md 同目录的 cover.jpg。
    与 get_book_covers 一致：返回 frontmatter 用的相对路径（cover.jpg）或 None。
    """
    base = os.path.splitext(os.path.basename(md_file_path))[0]
    if not base.strip():
        print("md 文件名为空，跳过谷歌备选")
        return None
    keyword = base.strip() + ' 书籍'
    image_url = _first_image_url_from_google(keyword)
    if not image_url:
        print(f"谷歌图片未找到结果: {keyword}")
        return None
    time.sleep(0.5)
    return _download_image_to_path(image_url, md_file_path)


def process_files():
    """递归处理目标文件夹中所有 md：无 cover 时用谷歌图片搜索下载封面。与 get_book_covers 行为一致。"""
    total_files = 0
    processed_files = 0
    skipped_files = 0

    for root, _dirs, files in os.walk(TARGET_FOLDER):
        for filename in files:
            if not filename.endswith('.md'):
                continue
            total_files += 1
            file_path = os.path.join(root, filename)
            print(f"处理文件 ({processed_files + skipped_files + 1}/{total_files}): {file_path}")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"读取文件失败: {file_path}, 错误: {str(e)}")
                skipped_files += 1
                continue

            cover_match = re.search(r'cover:\s*(.+)', content)
            if cover_match and cover_match.group(1).strip():
                print(f"cover 字段已有值，跳过: {file_path}")
                skipped_files += 1
                continue

            cover_value = fetch_and_download_cover_from_google(file_path)
            if not cover_value:
                skipped_files += 1
                continue

            # 与 get_book_covers 一致：更新 frontmatter 中的 cover
            try:
                from get_book_covers import update_cover_in_file
                if update_cover_in_file(file_path, cover_value):
                    processed_files += 1
                else:
                    skipped_files += 1
            except ImportError:
                processed_files += 1
            time.sleep(1.0)

    print(f"所有文件处理完成! 共 {total_files} 个文件，其中 {processed_files} 个已更新，{skipped_files} 个跳过。")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]) and sys.argv[1].endswith('.md'):
        result = fetch_and_download_cover_from_google(sys.argv[1])
        print(f"结果: {result}")
    else:
        process_files()
