import os
import re
import requests
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
from bs4 import BeautifulSoup

# 配置路径
TARGET_FOLDER = os.path.join(ROOT_DIR, '..', '读书')

# 请求头，模拟浏览器访问
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

def get_cover_image_url(douban_link):
    """从豆瓣链接获取封面图片URL"""
    try:
        # 发送请求
        response = requests.get(douban_link, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找封面图片 - 尝试多种方式
        # 方式1: 查找id为mainpic的元素
        mainpic_div = soup.find('div', id='mainpic')
        if mainpic_div:
            img_tag = mainpic_div.find('img')
            if img_tag and 'src' in img_tag.attrs:
                cover_url = img_tag['src']
            else:
                print(f"无法找到图片URL: {douban_link}")
                return None
        else:
            # 方式2: 查找class为book-cover的元素
            cover_div = soup.find('div', class_='book-cover')
            if cover_div:
                img_tag = cover_div.find('img')
                if img_tag and 'src' in img_tag.attrs:
                    cover_url = img_tag['src']
                else:
                    print(f"无法找到图片URL: {douban_link}")
                    return None
            else:
                # 方式3: 查找所有img标签，筛选alt包含书名的
                img_tags = soup.find_all('img')
                for img in img_tags:
                    if 'alt' in img.attrs and '封面' in img['alt']:
                        cover_url = img['src']
                        break
                else:
                    print(f"无法找到封面图片: {douban_link}")
                    return None
        
        # 确保URL是完整的
        if not cover_url.startswith('http'):
            cover_url = 'https:' + cover_url
        
        # 移除可能的尺寸限制参数
        if 's_' in cover_url:
            cover_url = cover_url.replace('s_', '')
        elif 'm_' in cover_url:
            cover_url = cover_url.replace('m_', '')
        elif '.jpg' in cover_url and '://' in cover_url:
            # 如果URL已经是完整的高清图，直接使用
            pass
        else:
            # 添加默认尺寸参数
            cover_url = cover_url.split('?')[0] + '?imageView2/1/w/500/h/750'
        
        return cover_url
    except Exception as e:
        print(f"获取封面图片失败: {douban_link}, 错误: {str(e)}")
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
            
            # 检查cover字段是否已有值
            cover_match = re.search(r'cover: (https://.*)', content)
            if cover_match and cover_match.group(1).strip():
                print(f"cover字段已有值，跳过文件: {file_path}")
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
            
            # 获取封面图片URL
            cover_url = get_cover_image_url(douban_link)
            if not cover_url:
                skipped_files += 1
                continue
            
            # 更新文件
            if update_cover_in_file(file_path, cover_url):
                processed_files += 1
            else:
                skipped_files += 1
    
    print(f"所有文件处理完成! 共处理 {total_files} 个文件，其中 {processed_files} 个文件已更新，{skipped_files} 个文件被跳过。")

if __name__ == '__main__':
    process_files()