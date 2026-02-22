import os
import re
import requests
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
from bs4 import BeautifulSoup

# 配置路径
TARGET_FOLDER = os.path.join(ROOT_DIR, '..', '读书')

# 请求头，模拟浏览器访问（豆瓣会校验 Referer，图片请求需带 book.douban.com）
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}
# 请求图片时需带 Referer，否则豆瓣 CDN 返回 418 拒绝
IMAGE_HEADERS = {
    **HEADERS,
    'Referer': 'https://book.douban.com/',
}

# 封面保存文件名（与 md 同目录）
COVER_FILENAME = 'cover.jpg'

def get_cover_image_url(douban_link):
    """从豆瓣链接获取封面图片 URL（用于下载，豆瓣禁止外链故需下载到本地使用）。"""
    try:
        response = requests.get(douban_link, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        cover_url = None
        # 方式1: id=mainpic，优先用父级 a.nbg 的 href（大图），否则用 img 的 src
        mainpic_div = soup.find('div', id='mainpic')
        if mainpic_div:
            nbg_a = mainpic_div.find('a', class_='nbg')
            if nbg_a and nbg_a.get('href'):
                cover_url = nbg_a['href']
            if not cover_url:
                img_tag = mainpic_div.find('img')
                if img_tag and img_tag.get('src'):
                    cover_url = img_tag['src']
                    # 豆瓣小图路径为 .../s/public/...，改为 l/public 得大图
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
            print(f"无法找到封面图片: {douban_link}")
            return None
        if not cover_url.startswith('http'):
            cover_url = 'https:' + cover_url
        return cover_url
    except Exception as e:
        print(f"获取封面图片失败: {douban_link}, 错误: {str(e)}")
        return None


def download_cover_to_local(cover_url, md_file_path):
    """
    用带 Referer 的请求下载封面到 md 所在目录，文件名为 cover.jpg。
    返回用于 frontmatter 的本地相对路径（相对该 md 文件），失败返回 None。
    """
    try:
        r = requests.get(cover_url, headers=IMAGE_HEADERS, timeout=15)
        r.raise_for_status()
        content_type = r.headers.get('Content-Type', '')
        if 'image' not in content_type:
            print(f"非图片响应: {cover_url}, Content-Type: {content_type}")
            return None
        folder = os.path.dirname(md_file_path)
        os.makedirs(folder, exist_ok=True)
        local_path = os.path.join(folder, COVER_FILENAME)
        with open(local_path, 'wb') as f:
            f.write(r.content)
        # frontmatter 里使用相对当前 md 的路径，同目录即文件名
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

            # 获取封面图片 URL 并下载到本地（豆瓣禁止外链，直接写 URL 会 418）
            cover_url = get_cover_image_url(douban_link)
            if not cover_url:
                skipped_files += 1
                continue
            cover_value = download_cover_to_local(cover_url, file_path)
            if not cover_value:
                skipped_files += 1
                continue

            # 更新文件中的 cover 为本地路径
            if update_cover_in_file(file_path, cover_value):
                processed_files += 1
            else:
                skipped_files += 1
    
    print(f"所有文件处理完成! 共处理 {total_files} 个文件，其中 {processed_files} 个文件已更新，{skipped_files} 个文件被跳过。")

def test_single_url(douban_link, save_dir=None):
    """仅测试：从豆瓣链接获取并下载封面到指定目录。不处理 md 文件。"""
    save_dir = save_dir or ROOT_DIR
    md_dummy = os.path.join(save_dir, '_dummy.md')
    print(f"测试链接: {douban_link}")
    cover_url = get_cover_image_url(douban_link)
    if not cover_url:
        print("获取封面 URL 失败")
        return
    print(f"封面 URL: {cover_url}")
    local = download_cover_to_local(cover_url, md_dummy)
    if local:
        print(f"已保存为: {os.path.join(save_dir, COVER_FILENAME)}")
    else:
        print("下载封面失败")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1].startswith('http'):
        test_single_url(sys.argv[1])
    else:
        process_files()