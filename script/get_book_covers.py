import os
import re
import time
import requests
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
from bs4 import BeautifulSoup

# 配置路径
TARGET_FOLDER = os.path.join(ROOT_DIR, '..', '读书')

# 请求头，尽量贴近浏览器（豆瓣会校验 Referer/来源，否则易 418）
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}
# 请求图片时必须带书籍页 Referer
IMAGE_REFERER_HEADERS = {'Referer': 'https://book.douban.com/'}

# 封面保存文件名（与 md 同目录）
COVER_FILENAME = 'cover.jpg'


def _parse_cover_url_from_soup(soup, douban_link):
    """从已解析的 soup 中解析封面 URL。"""
    cover_url = None
    mainpic_div = soup.find('div', id='mainpic')
    if mainpic_div:
        nbg_a = mainpic_div.find('a', class_='nbg')
        if nbg_a and nbg_a.get('href'):
            cover_url = nbg_a['href']
        if not cover_url:
            img_tag = mainpic_div.find('img')
            if img_tag and img_tag.get('src'):
                cover_url = img_tag['src']
                if '/s/public/' in cover_url:
                    cover_url = cover_url.replace('/s/public/', '/l/public/')
    if not cover_url:
        cover_div = soup.find('div', class_='book-cover')
        if cover_div:
            img_tag = cover_div.find('img')
            if img_tag and img_tag.get('src'):
                cover_url = img_tag['src']
                if '/s/public/' in cover_url:
                    cover_url = cover_url.replace('/s/public/', '/l/public/')
    if not cover_url:
        for img in soup.find_all('img'):
            if img.get('alt') and '封面' in img['alt'] and img.get('src'):
                cover_url = img['src']
                if '/s/public/' in cover_url:
                    cover_url = cover_url.replace('/s/public/', '/l/public/')
                break
    if not cover_url:
        return None
    if not cover_url.startswith('http'):
        cover_url = 'https:' + cover_url
    return cover_url


def _do_fetch_and_download(session, douban_link, md_file_path):
    """内部：请求书籍页 → 解析封面 URL → 请求图片。同一 Session 带 Referer。返回 COVER_FILENAME 或 None。"""
    # 1. 请求书籍页（Referer 为豆瓣读书首页，避免 418）
    session.headers['Referer'] = 'https://book.douban.com/'
    r_page = session.get(douban_link, timeout=15)
    r_page.raise_for_status()
    soup = BeautifulSoup(r_page.text, 'html.parser')
    cover_url = _parse_cover_url_from_soup(soup, douban_link)
    if not cover_url:
        return None
    # 2. 请求图片时 Referer 为书籍页，并标明为图片请求
    time.sleep(1)
    img_headers = {'Referer': douban_link, 'Sec-Fetch-Dest': 'image'}
    r_img = session.get(cover_url, headers=img_headers, timeout=15)
    r_img.raise_for_status()
    if 'image' not in (r_img.headers.get('Content-Type') or ''):
        return None
    folder = os.path.dirname(md_file_path)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, COVER_FILENAME), 'wb') as f:
        f.write(r_img.content)
    return COVER_FILENAME


def fetch_and_download_cover(douban_link, md_file_path):
    """
    用同一 Session：先访问豆瓣读书首页 → 书籍页 → 封面图，避免 418。
    封面保存到 md 所在目录的 cover.jpg。遇 418 会重试一次。
    返回 frontmatter 用的相对路径（cover.jpg）或 None。
    """
    session = requests.Session()
    session.headers.update(HEADERS)
    for attempt in range(2):
        try:
            result = _do_fetch_and_download(session, douban_link, md_file_path)
            if result:
                return result
            if attempt == 0:
                print(f"无法从页面解析封面: {douban_link}")
            return None
        except requests.HTTPError as e:
            if e.response.status_code != 418:
                print(f"请求失败: {e.response.status_code} {e.response.reason} - {douban_link}")
                return None
            if attempt == 0:
                print(f"418 被拒绝，3 秒后重试一次: {douban_link}")
                time.sleep(3)
                continue
            print(f"请求失败: 418 - {douban_link}（豆瓣反爬/限流，可稍后再试或检查网络）")
            return None
        except Exception as e:
            print(f"获取或下载封面失败: {douban_link}, 错误: {str(e)}")
            return None
    return None


def get_cover_image_url(douban_link):
    """从豆瓣链接获取封面图片 URL（仅解析用；实际下载请用 fetch_and_download_cover）。"""
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        response = session.get(douban_link, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return _parse_cover_url_from_soup(soup, douban_link)
    except Exception as e:
        print(f"获取封面图片失败: {douban_link}, 错误: {str(e)}")
        return None


def download_cover_to_local(cover_url, md_file_path, referer=None):
    """
    用带 Referer 的请求下载封面到 md 所在目录，文件名为 cover.jpg。
    建议优先使用 fetch_and_download_cover，以同一 Session 避免 418。
    """
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        image_headers = {'Referer': referer or 'https://book.douban.com/'}
        r = session.get(cover_url, headers=image_headers, timeout=15)
        r.raise_for_status()
        content_type = r.headers.get('Content-Type', '')
        if 'image' not in content_type:
            print(f"非图片响应: {cover_url}, Content-Type: {content_type}")
            return None
        folder = os.path.dirname(md_file_path)
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, COVER_FILENAME), 'wb') as f:
            f.write(r.content)
        return COVER_FILENAME
    except Exception as e:
        print(f"下载封面失败: {cover_url}, 错误: {str(e)}")
        return None

def update_cover_in_file(file_path, cover_url):
    """更新文件中的cover字段，只修改YAML frontmatter部分，保留完整正文"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分割YAML frontmatter和正文内容
        if content.startswith('---'):
            # 查找YAML结束的位置
            yaml_end = content.find('---', 3)
            if yaml_end != -1:
                # 提取YAML部分和正文部分
                yaml_content = content[:yaml_end + 3]
                main_content = content[yaml_end + 3:]
                
                # 只在YAML部分中替换cover字段
                pattern = r'cover:.*'
                updated_yaml = re.sub(pattern, f'cover: {cover_url}', yaml_content)
                
                # 重新组合文件内容
                new_content = updated_yaml + main_content
            else:
                # 如果没有找到结束的---，就在整个内容中替换cover字段
                pattern = r'cover:.*'
                new_content = re.sub(pattern, f'cover: {cover_url}', content)
        else:
            # 如果没有YAML frontmatter，就在整个内容中替换cover字段
            pattern = r'cover:.*'
            new_content = re.sub(pattern, f'cover: {cover_url}', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"已更新文件: {file_path}")
        return True
    except Exception as e:
        print(f"更新文件失败: {file_path}, 错误: {str(e)}")
        return False

def process_files():
    """递归处理目标文件夹及其所有子文件夹中的md文件"""
    # 统计信息
    total_files = 0
    processed_files = 0
    skipped_files = 0
    
    # 使用os.walk递归遍历所有文件夹
    for root, dirs, files in os.walk(TARGET_FOLDER):
        for filename in files:
            if not filename.endswith('.md'):
                continue
            
            total_files += 1
            file_path = os.path.join(root, filename)
            print(f"处理文件 ({processed_files + skipped_files + 1}/{total_files}): {file_path}")
            
            # 读取文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"读取文件失败: {file_path}, 错误: {str(e)}")
                skipped_files += 1
                continue
            
            # 检查 cover 字段是否已有值（URL 或本地路径都视为已有）
            cover_match = re.search(r'cover:\s*(.+)', content)
            if cover_match and cover_match.group(1).strip():
                print(f"cover 字段已有值，跳过文件: {file_path}")
                skipped_files += 1
                continue

            # 提取豆瓣链接
            douban_match = re.search(r'douban_link: (https://book\.douban\.com/subject/\d+/)', content)
            if not douban_match:
                print(f"未找到豆瓣链接: {file_path}")
                skipped_files += 1
                continue

            douban_link = douban_match.group(1)
            print(f"找到豆瓣链接: {douban_link}")

            # 用同一 Session 先访问书籍页再下载封面，避免 418
            cover_value = fetch_and_download_cover(douban_link, file_path)
            if not cover_value:
                try:
                    from get_book_cover_from_google import fetch_and_download_cover_from_google
                    print(f"豆瓣未获取到封面，尝试谷歌图片备选: {file_path}")
                    cover_value = fetch_and_download_cover_from_google(file_path)
                except ImportError:
                    pass
            if not cover_value:
                skipped_files += 1
                continue

            # 更新文件中的 cover 为本地路径
            if update_cover_in_file(file_path, cover_value):
                processed_files += 1
            else:
                skipped_files += 1
            # 多本书之间稍作间隔，降低被限流/418 概率
            time.sleep(1.5)

    print(f"所有文件处理完成! 共处理 {total_files} 个文件，其中 {processed_files} 个文件已更新，{skipped_files} 个文件被跳过。")

def test_single_url(douban_link, save_dir=None):
    """仅测试：从豆瓣链接获取并下载封面到指定目录。不处理 md 文件。"""
    save_dir = save_dir or ROOT_DIR
    md_dummy = os.path.join(save_dir, '_dummy.md')
    print(f"测试链接: {douban_link}")
    local = fetch_and_download_cover(douban_link, md_dummy)
    if local:
        print(f"已保存为: {os.path.join(save_dir, COVER_FILENAME)}")
    else:
        print("获取或下载封面失败")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1].startswith('http'):
        test_single_url(sys.argv[1])
    else:
        process_files()