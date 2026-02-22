import os
import re
import time
import requests
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 配置路径
TARGET_FOLDER = os.path.join(ROOT_DIR, '..', '读书')
IMG_FOLDER = os.path.join(ROOT_DIR, '..', 'img')

# 请求头，尽量贴近浏览器（豆瓣等会校验 Referer，否则易 418）
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'image',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'none',
}

# 统计信息
total_files = 0
processed_files = 0
skipped_files = 0
downloaded_count = 0
existed_count = 0

def create_img_folder():
    """创建img文件夹"""
    if not os.path.exists(IMG_FOLDER):
        os.makedirs(IMG_FOLDER)
        print(f"已创建图片文件夹: {IMG_FOLDER}")
    else:
        print(f"图片文件夹已存在: {IMG_FOLDER}")

def extract_cover_url(content):
    """从文件内容中提取cover字段的URL"""
    # 查找YAML frontmatter
    if content.startswith('---'):
        yaml_end = content.find('---', 3)
        if yaml_end != -1:
            yaml_content = content[:yaml_end + 3]
        else:
            yaml_content = content
    else:
        yaml_content = content
    
    # 提取cover URL
    cover_match = re.search(r'cover:\s*(https://.*?)(?:\n|$)', yaml_content)
    if cover_match:
        return cover_match.group(1).strip()
    
    return None

def _is_douban_image_url(url):
    """判断是否为豆瓣图片链接（需带 Referer 否则易 418）"""
    return 'douban.com' in url or 'doubanio.com' in url


def download_image(image_url, save_path):
    """下载图片并保存到指定路径。豆瓣图源带 Referer 并支持 418 重试。"""
    session = requests.Session()
    session.headers.update(HEADERS)
    # 豆瓣图源必须带 Referer，否则易被拒绝
    if _is_douban_image_url(image_url):
        session.headers['Referer'] = 'https://book.douban.com/'
    for attempt in range(2):
        try:
            r = session.get(image_url, timeout=15, stream=True)
            r.raise_for_status()
            ct = (r.headers.get('Content-Type') or '').lower()
            if 'image' not in ct and 'octet-stream' not in ct:
                print(f"非图片响应: {image_url[:80]}..., Content-Type: {ct}")
                return False
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except requests.HTTPError as e:
            if e.response.status_code == 418 and attempt == 0:
                print(f"418 被拒绝，3 秒后重试: {image_url[:60]}...")
                time.sleep(3)
                continue
            print(f"下载图片失败: {image_url}, HTTP {e.response.status_code} {e.response.reason}")
            return False
        except Exception as e:
            print(f"下载图片失败: {image_url}, 错误: {str(e)}")
            return False
    return False

def download_book_covers():
    """下载所有书籍封面图片"""
    global total_files, processed_files, skipped_files, downloaded_count, existed_count
    
    # 创建img文件夹
    create_img_folder()
    
    # 使用os.walk递归遍历所有文件夹
    for root, dirs, files in os.walk(TARGET_FOLDER):
        for filename in files:
            if not filename.endswith('.md'):
                continue
            
            total_files += 1
            file_path = os.path.join(root, filename)
            print(f"处理文件 ({processed_files + skipped_files + 1}): {file_path}")
            
            # 读取文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"读取文件失败: {file_path}, 错误: {str(e)}")
                skipped_files += 1
                continue
            
            # 提取cover URL
            cover_url = extract_cover_url(content)
            if not cover_url:
                print(f"未找到封面链接，跳过文件: {file_path}")
                skipped_files += 1
                continue
            
            # 构建图片保存路径
            book_name = os.path.splitext(filename)[0]  # 去掉.md扩展名
            # 确保图片扩展名正确
            image_extension = cover_url.split('.')[-1].split('?')[0].lower()
            if image_extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                image_extension = 'jpg'  # 默认使用jpg扩展名
            
            save_path = os.path.join(IMG_FOLDER, f"{book_name}.{image_extension}")
            
            # 检查图片是否已存在
            if os.path.exists(save_path):
                print(f"图片已存在，跳过下载: {save_path}")
                existed_count += 1
                processed_files += 1
                continue
            
            # 下载图片
            print(f"下载图片: {cover_url} -> {save_path}")
            if download_image(cover_url, save_path):
                downloaded_count += 1
                processed_files += 1
                if _is_douban_image_url(cover_url):
                    time.sleep(1.0)  # 豆瓣图源稍作间隔，降低限流概率
            else:
                skipped_files += 1
    
    print(f"\n封面图片下载完成！")
    print(f"共处理 {total_files} 个文件，其中 {processed_files} 个文件已处理，{skipped_files} 个文件被跳过。")
    print(f"新下载图片: {downloaded_count} 张，已存在图片: {existed_count} 张。")

if __name__ == '__main__':
    download_book_covers()