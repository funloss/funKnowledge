import os
import re

# 定义根目录
root_dir = '/Users/zhezhang/Documents/Fun Knowledge/读书'

def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已有属性块
        if content.startswith('---'):
            # 查找属性块的结束位置
            end_match = re.search(r'^---', content[3:], re.MULTILINE)
            if end_match:
                end_pos = 3 + end_match.start()
                properties = content[:end_pos]
                rest_content = content[end_pos:]
                
                # 检查是否已经有score标签
                if 'score:' in properties:
                    print(f"已存在score标签: {file_path}")
                    return
                
                # 在douban_link下面添加score标签
                updated_properties = re.sub(r'(douban_link:.*?)\n', '\\1\nscore: 4\n', properties)
                
                # 如果没有找到douban_link，就在cover下面添加
                if updated_properties == properties:
                    updated_properties = re.sub(r'(cover:.*?)\n', '\\1\nscore: 4\n', properties)
                    
                # 如果仍然没有更新，说明属性块格式不同，直接在属性块末尾添加
                if updated_properties == properties:
                    # 确保正确处理换行符
                    score_line = 'score: 4\n'
                    updated_properties = properties.replace('---', score_line + '---')
                
                updated_content = updated_properties + rest_content
                
                # 写回文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print(f"已添加score标签: {file_path}")
            else:
                print(f"属性块格式不正确: {file_path}")
        else:
            print(f"没有属性块: {file_path}")
    except Exception as e:
        print(f"处理文件出错 {file_path}: {str(e)}")

def traverse_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                process_file(file_path)

if __name__ == '__main__':
    traverse_directory(root_dir)
    print("所有文件处理完成！")