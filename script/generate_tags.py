import os
from openai import OpenAI

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def call_llm(prompt):
    """调用大模型获取响应"""
    client = OpenAI(
        api_key="sk-11ec62a50c9a4862a1e490e6ea07fc54",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    completion = client.chat.completions.create(
        model="deepseek-r1",
        messages=[
            {'role': 'user', 'content': prompt}
        ]
    )

    result = completion.choices[0].message.content
    return result

def generate_tags(md_file_path):
    """
    为markdown文件生成并更新tags
    参数: md_file_path - markdown文件的路径
    功能: 检查tag数量，调用大模型生成新标签，更新文件中的tags
    """
    # 检查文件是否存在
    if not os.path.exists(md_file_path):
        print(f"错误：找不到文件 {md_file_path}")
        return

    # 读取文件内容
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.readlines()

    # 查找tags部分
    tags_start_index = -1
    tags_end_index = -1
    tags_lines = []
    
    for i, line in enumerate(content):
        stripped_line = line.strip()
        if stripped_line == 'tags:':
            tags_start_index = i
        elif tags_start_index != -1 and tags_end_index == -1 and stripped_line and not stripped_line.startswith('- '):
            tags_end_index = i
            break
    
    # 如果没有找到tags部分，在文件开头添加
    if tags_start_index == -1:
        print(f"文件中未找到tags部分，将在开头添加")
        # 找到第一个---分隔符的位置
        first_separator = -1
        for i, line in enumerate(content):
            if line.strip() == '---':
                first_separator = i
                break
        
        if first_separator != -1:
            # 在第一个---前插入tags部分
            content.insert(first_separator, 'tags:\n')
            content.insert(first_separator + 1, '  - 标签1\n')
            content.insert(first_separator + 2, '  - 标签2\n')
            content.insert(first_separator + 3, '  - 标签3\n')
            tags_start_index = first_separator
            tags_end_index = first_separator + 4
        else:
            # 如果没有分隔符，在文件开头添加
            content.insert(0, 'tags:\n')
            content.insert(1, '  - 标签1\n')
            content.insert(2, '  - 标签2\n')
            content.insert(3, '  - 标签3\n')
            content.insert(4, '---\n')
            content.insert(5, '\n')
            tags_start_index = 0
            tags_end_index = 5
    
    # 提取当前的tags
    if tags_end_index == -1:
        tags_end_index = len(content)
    
    current_tags = []
    for i in range(tags_start_index + 1, tags_end_index):
        line = content[i].strip()
        if line.startswith('- '):
            tag = line[2:].strip()
            if tag:
                current_tags.append(tag)
    
    # 检查tags数量是否大于3
    if len(current_tags) > 3:
        print(f"文件 {md_file_path} 中的tags数量已大于3，无需更新")
        return
    
    # 读取文件的主要内容用于生成tags
    full_content = ''.join(content)
    
    # 查找【章节内容】标记，并只使用其后的内容
    section_marker = '章节内容'
    section_start_index = full_content.find(section_marker)
    if section_start_index != -1:
        # 只使用【章节内容】之后的部分
        main_content = full_content[section_start_index + len(section_marker):]
    else:
        # 如果没有找到【章节内容】标记，则使用整个内容
        print(f"警告：文件 {md_file_path} 中未找到【章节内容】标记，将使用整个文件内容")
        main_content = full_content
    
    # 构建prompt
    prompt = f"""我需要你为一篇关于历史的读书笔记生成5个相关的标签。\n\n请你基于文章内容，生成5个最相关的标签，要求：\n1. 标签要简洁明了，从基础事实出发，能够准确反映文章的主题和内容\n2. 避免过于宽泛和空洞的标签\n3. 请只返回标签，不要有其他解释，每个标签一行\n4. 标签用中文表示\n5.每个标签最多不超过8个字\n\n【文章内容】：{main_content[:20000]}..."""
    
    # 调用大模型生成tags
    print(f"正在为 {md_file_path} 生成标签...")
    generated_tags_text = call_llm(prompt)
    
    # 解析生成的tags
    generated_tags = []
    for line in generated_tags_text.strip().split('\n'):
        tag = line.strip()
        if tag and tag not in generated_tags:
            generated_tags.append(tag)
    
    # 限制生成的tags数量为5个
    generated_tags = generated_tags[:5]
    
    # 合并当前tags和生成的tags，避免重复
    all_tags = list(set(current_tags + generated_tags))
    
    # 准备更新后的tags部分
    updated_tags_lines = ['tags:\n']
    for tag in all_tags:
        updated_tags_lines.append(f'  - {tag}\n')
    
    # 更新文件内容
    new_content = content[:tags_start_index] + updated_tags_lines + content[tags_end_index:]
    
    # 写回文件
    with open(md_file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_content)
    
    print(f"已成功更新 {md_file_path} 的tags，新标签：{', '.join(all_tags)}")

def get_all_md_files(folder_path):
    """
    获取指定目录及其子目录下的所有markdown文件
    参数: folder_path - 要搜索的目录路径
    返回: 包含所有md文件绝对路径的列表
    """
    md_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    return md_files

if __name__ == '__main__':
    # 设置读书目录路径
    books_dir = os.path.join(ROOT_DIR, '..', '读书')
    
    # 获取所有markdown文件
    all_md_files = get_all_md_files(books_dir)
    
    print(f"找到 {len(all_md_files)} 个markdown文件需要处理")
    
    # 遍历处理每个文件
    processed_count = 0
    skipped_count = 0
    
    for md_file_path in all_md_files:
        try:
            # 检查文件大小，避免处理空文件
            if os.path.getsize(md_file_path) == 0:
                print(f"跳过空文件: {md_file_path}")
                skipped_count += 1
                continue
                
            generate_tags(md_file_path)
            processed_count += 1
        except Exception as e:
            print(f"处理文件 {md_file_path} 时出错: {str(e)}")
            skipped_count += 1
    
    # 输出总结信息
    print("="*50)
    print(f"处理完成！")
    print(f"成功处理: {processed_count} 个文件")
    print(f"跳过/失败: {skipped_count} 个文件")
    print(f"总计: {len(all_md_files)} 个文件")
    print("="*50)