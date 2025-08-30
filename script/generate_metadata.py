import os
import re
import json
import datetime
import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 配置路径
TARGET_FOLDER = os.path.join(ROOT_DIR, '..', '读书')
OUTPUT_FILE = os.path.join(ROOT_DIR, '..', 'metaData.json')
GITHUB_BASE_URL = 'https://github.com/funloss/funKnowledge/blob/main/'

# 统计信息
total_files = 0
processed_files = 0
skipped_files = 0
metadata_list = []

def extract_frontmatter_data(content):
    """从文件内容中提取YAML frontmatter中的douban_link, cover, score和tags字段"""
    douban_url = None
    book_cover = None
    score = None
    tags = []
    
    # 查找YAML frontmatter
    if content.startswith('---'):
        yaml_end = content.find('---', 3)
        if yaml_end != -1:
            yaml_content = content[:yaml_end + 3]
        else:
            yaml_content = content
    else:
        yaml_content = content
    
    # 提取douban_link
    douban_match = re.search(r'douban_link:\s*(https://book\.douban\.com/subject/\d+/)', yaml_content)
    if douban_match:
        douban_url = douban_match.group(1)
    
    # 提取cover
    cover_match = re.search(r'cover:\s*(https://.*?)(?:\n|$)', yaml_content)
    if cover_match:
        book_cover = cover_match.group(1)
    
    # 提取score
    score_match = re.search(r'score:\s*(\d+(?:\.\d+)?)', yaml_content)
    if score_match:
        score = float(score_match.group(1))
    
    # 提取tags
    # 查找tags:部分
    tags_section_match = re.search(r'tags:\s*\n([\s\S]*?)(?=\n[^\s-]|\Z)', yaml_content)
    if tags_section_match:
        tags_section = tags_section_match.group(1)
        # 提取所有以-开头的标签
        tag_matches = re.findall(r'-\s*(\S+)', tags_section)
        tags = tag_matches
    
    return douban_url, book_cover, score, tags

def generate_github_url(file_path):
    """生成GitHub URL"""
    # 获取相对于TARGET_FOLDER的路径
    relative_path = os.path.relpath(file_path, os.path.dirname(TARGET_FOLDER))
    # 构建完整的GitHub URL
    github_url = GITHUB_BASE_URL + relative_path
    return github_url

def get_category_info(file_path):
    """获取分类信息：cate_level1和cate_leaf"""
    # 获取相对于TARGET_FOLDER的路径
    relative_path = os.path.relpath(file_path, TARGET_FOLDER)
    
    # 分割路径
    path_parts = relative_path.split(os.sep)
    
    # 获取一级分类（读书目录下的下一级目录）
    if len(path_parts) > 1:
        cate_level1 = path_parts[0]
    else:
        # 如果文件直接在读书目录下，一级分类为"首页"
        cate_level1 = "首页"
    
    # 获取叶子分类（文件的上一级目录）
    if len(path_parts) > 1:
        # 叶子分类是倒数第二个目录
        if len(path_parts) > 2:
            cate_leaf = path_parts[-2]
        else:
            # 如果文件直接在一级分类目录下，叶子分类就是一级分类
            cate_leaf = path_parts[0]
    else:
        # 如果文件直接在读书目录下，叶子分类为"首页"
        cate_leaf = "首页"
    
    return cate_level1, cate_leaf

def generate_metadata():
    """生成书籍元数据JSON文件"""
    global total_files, processed_files, skipped_files, metadata_list
    
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
            
            # 提取书籍信息
            book_name = os.path.splitext(filename)[0]  # 去掉.md扩展名
            douban_url, _, score, tags = extract_frontmatter_data(content)  # 提取tags字段
            
            # 检查必要字段
            if not douban_url:
                print(f"未找到豆瓣链接，跳过文件: {file_path}")
                skipped_files += 1
                continue
            
            # 获取分类信息
            cate_level1, cate_leaf = get_category_info(file_path)
            
            # 生成GitHub URL
            github_url = generate_github_url(file_path)
            
            # 创建GitHub图片链接（raw格式）
            github_cover_url = f"https://raw.githubusercontent.com/funloss/funKnowledge/main/img/{book_name}.jpg"
            
            # 获取文件的创建时间
            try:
                # 在macOS上，使用os.stat获取birthtime作为创建时间
                stat_info = os.stat(file_path)
                # macOS系统上使用birthtime
                ctime = stat_info.st_birthtime
                # 转换为格式化的日期字符串（YYYY-MM-DD）
                mtime_str = datetime.datetime.fromtimestamp(ctime).strftime('%Y-%m-%d')
            except Exception as e:
                print(f"获取文件创建时间失败: {file_path}, 错误: {str(e)}")
                mtime_str = None
            
            # 创建书籍元数据对象
            book_metadata = {
                "bookName": book_name,
                "doubanUrl": douban_url,
                "bookCover": github_cover_url,  # 使用GitHub图片链接
                "cate_level1": cate_level1,
                "cate_leaf": cate_leaf,
                "githubUrl": github_url,
                "score": score,  # 添加score字段
                "mtime": mtime_str,  # 添加mtime字段（文件创建日期）
                "tags": tags  # 添加tags字段，值为标签字符串数组
            }
            
            # 添加到列表
            metadata_list.append(book_metadata)
            processed_files += 1
    
    # 写入JSON文件
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata_list, f, ensure_ascii=False, indent=2)
        print(f"\n元数据生成完成！已写入文件: {OUTPUT_FILE}")
        print(f"共处理 {total_files} 个文件，其中 {processed_files} 个文件已处理，{skipped_files} 个文件被跳过。")
    except Exception as e:
        print(f"写入JSON文件失败: {str(e)}")

if __name__ == '__main__':
    generate_metadata()