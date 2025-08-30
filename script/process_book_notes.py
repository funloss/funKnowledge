import os
import re
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 定义根目录
root_dir = os.path.join(ROOT_DIR, '..', '读书')

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 提取豆瓣链接
    douban_link_match = re.search(r'豆瓣链接：(https?://book\.douban\.com/subject/\d+/)', content)
    if not douban_link_match:
        print(f"未找到豆瓣链接: {file_path}")
        return
    
    douban_link = douban_link_match.group(1)
    
    # 检查是否已有笔记属性
    if content.startswith('---'):
        # 已有属性块，更新douban_link
        updated_content = re.sub(r'douban_link:\s*(.*)', f'douban_link: {douban_link}', content)
        # 移除原来的豆瓣链接行
        updated_content = re.sub(r'豆瓣链接：https?://book\.douban\.com/subject/\d+/\n?', '', updated_content)
    else:
        # 没有属性块，添加属性块
        # 移除原来的豆瓣链接行
        content_without_link = re.sub(r'豆瓣链接：https?://book\.douban\.com/subject/\d+/\n?', '', content)
        # 添加属性块
        updated_content = f'---\ntags:\ndouban_link: {douban_link}\n---\n{content_without_link}'
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"已处理: {file_path}")

def traverse_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                process_file(file_path)
if __name__ == '__main__':
    traverse_directory(root_dir)
    print("所有文件处理完成！")