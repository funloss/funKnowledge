import os
import re
import requests

# 配置路径
TARGET_FOLDER = '/Users/zhezhang/Documents/Fun Knowledge/读书'
IMG_FOLDER = '/Users/zhezhang/Documents/Fun Knowledge/img'

# 请求头，模拟浏览器访问
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
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

def download_image(image_url, save_path):
    """下载图片并保存到指定路径"""
    try:
        # 发送请求
        response = requests.get(image_url, headers=HEADERS, timeout=10, stream=True)
        response.raise_for_status()
        
        # 保存图片
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"下载图片失败: {image_url}, 错误: {str(e)}")
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
            else:
                skipped_files += 1
    
    print(f"\n封面图片下载完成！")
    print(f"共处理 {total_files} 个文件，其中 {processed_files} 个文件已处理，{skipped_files} 个文件被跳过。")
    print(f"新下载图片: {downloaded_count} 张，已存在图片: {existed_count} 张。")

if __name__ == '__main__':
    download_book_covers()