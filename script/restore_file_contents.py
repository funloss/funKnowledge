import os
import shutil
import json
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
from datetime import datetime

# 配置路径
TARGET_FOLDER = os.path.join(ROOT_DIR, '..', '读书', '文学作品', '陀思妥耶夫斯基')
BACKUP_FOLDER = os.path.join(ROOT_DIR, '..', '读书', '文学作品', '陀思妥耶夫斯基_backup')

# 需要恢复的文件及其预期内容结构
# 这里列出的是基于之前查看的内容和类似文件的结构
EXPECTED_FILES = {
    '卡拉马佐夫兄弟.md': {
        'yaml': {
            'tags': '',
            'douban_link': 'https://book.douban.com/subject/25887924/',
            'cover': 'https://img9.doubanio.com/view/subject/s/public/s34711695.jpg'
        },
        'content': '''

```mermaid
mindmap
  root(卡拉马佐夫兄弟)
    人性悖论
      善恶共生光谱
      天使与野兽共存
      道德面具脆弱性
      葱头寓言救赎论
    
    信仰锚点
      佐西马实践之爱
      伊万理性反叛
      宗教大法官困境
      破碎中寻超越性
    
    救赎路径
      德米特里自我放逐
      阿辽沙大地忏悔
      责任绑定苦难
      挣脱存在虚无
    
    边缘隐喻
      怪物社会预言
        ⇨ 弑父的阶级压迫
```'''
    },
    '地下室手记.md': {
        'yaml': {
            'tags': '',
            'douban_link': 'https://book.douban.com/subject/34990839/',
            'cover': 'https://img3.doubanio.com/view/subject/s/public/s33638812.jpg'
        },
        'content': '''
# 深层解构

## 人性的矛盾深渊

### 基石：作者反复回归的核心信念

陀思妥耶夫斯基在《地下室手记》中构建的思想基石是：**人的本质不仅是理性的，更是充满矛盾、非理性和自我毁灭倾向的存在**。这一信念贯穿全书，构成了对19世纪理性主义哲学的有力批判。

*   **对“理性人”假设的彻底否定**：地下室人（主角）对当时流行的功利主义哲学（认为人总是会做出对自己最有利的理性选择）进行了辛辣的嘲讽。他宣称：“人最喜爱的就是制造混乱”，“人有时甚至会故意选择对自己有害的东西，只是为了证明自己的自由意志”。 这一论点指向了一个根本性的问题：如果人本质上是非理性的，那么建立在“理性人”假设上的社会秩序和道德准则，是否从根本上就是脆弱的？
*   **自由意志的悖论**：地下室人对自由的追求是病态的。他拒绝任何形式的束缚，包括他人的好意、社会的规范，甚至是自己的利益。这种极端的自由追求最终将他推向了自我封闭的“地下室”。 陀思妥耶夫斯基通过这个形象揭示了一个残酷的真相：**绝对的自由并非幸福，反而可能是一种难以承受的重负**。

### 边缘：思想曲线的远端洞见

在主要论证的边缘，作者触及了一些更具前瞻性的思想，它们超越了19世纪的语境，至今仍发人深省。

*   **自我意识的监狱**：地下室人的自我意识过于发达，他时刻在观察、分析、评判自己和他人的每一个行为和念头。这种过度的自我意识使他陷入了一种无法行动的瘫痪状态。 他渴望被爱，却又因为害怕被拒绝而先发制人地伤害别人；他渴望与社会连接，却又因为害怕暴露自己的脆弱而选择孤立。 这一形象预言了现代社会中许多人的精神困境——**过度的自我意识可能成为囚禁灵魂的监狱**。
*   **“屈辱的荣耀”**：地下室人反复强调，他从自己的苦难和屈辱中获得了一种扭曲的满足感。他说：“我甚至喜欢自己的痛苦，我喜欢咀嚼它们，从中得到乐趣。” 这种对痛苦的“享受”揭示了人类心理中一个被现代心理学证实的现象——**人在某些情况下会通过制造痛苦来获得存在感或控制感**。

### 暗流：未被言说的前提

全书的论证依赖于一个未被明言的假设，这是陀思妥耶夫斯基思想的底色，也是理解这部作品的关键。

*   **人性本恶，但仍有救赎可能**：尽管地下室人展现了人性中最黑暗、最扭曲的一面，尽管陀思妥耶夫斯基对理性主义进行了无情的批判，但在字里行间，你仍能感受到作者对人性的深切关怀。 地下室人的自我剖析虽然残酷，却充满了真诚；他的自我毁灭虽然绝望，却暗含着对救赎的隐秘渴望。 这暗示着，陀思妥耶夫斯基虽然不相信理性能够拯救人类，但他可能相信，**通过直面自己的黑暗面，通过对苦难的承担和对他者的爱，人类仍有获得救赎的可能**。 这一暗流，将在他后来的作品（如《罪与罚》《卡拉马佐夫兄弟》）中成为奔涌的主流。

---
'''
    }
}

def create_backup():
    """创建文件备份，防止进一步数据丢失"""
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)
        print(f"创建备份文件夹: {BACKUP_FOLDER}")
    
    for filename in os.listdir(TARGET_FOLDER):
        if not filename.endswith('.md'):
            continue
        
        src_path = os.path.join(TARGET_FOLDER, filename)
        dst_path = os.path.join(BACKUP_FOLDER, f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak")
        
        try:
            shutil.copy2(src_path, dst_path)
            print(f"已备份: {filename}")
        except Exception as e:
            print(f"备份文件失败: {filename}, 错误: {str(e)}")

def restore_file_content(file_path, yaml_data, expected_content):
    """恢复文件内容，保留正确的YAML frontmatter并添加预期的正文内容"""
    try:
        # 构建YAML frontmatter
        yaml_lines = ['---']
        for key, value in yaml_data.items():
            yaml_lines.append(f'{key}: {value}')
        yaml_lines.append('---')
        yaml_content = '\n'.join(yaml_lines)
        
        # 组合完整内容
        full_content = yaml_content + expected_content
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"已恢复文件内容: {file_path}")
        return True
    except Exception as e:
        print(f"恢复文件失败: {file_path}, 错误: {str(e)}")
        return False

def restore_all_files():
    """恢复所有目标文件的内容"""
    # 首先创建备份
    create_backup()
    
    # 然后恢复文件内容
    for filename, data in EXPECTED_FILES.items():
        file_path = os.path.join(TARGET_FOLDER, filename)
        if os.path.exists(file_path):
            # 读取当前文件内容，保留实际的cover链接
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    current_content = f.read()
                
                # 提取当前的cover链接
                import re
                cover_match = re.search(r'cover: (https://.*)', current_content)
                if cover_match:
                    data['yaml']['cover'] = cover_match.group(1)
            except:
                pass
            
            # 恢复文件内容
            restore_file_content(file_path, data['yaml'], data['content'])
        else:
            print(f"文件不存在: {file_path}")
    
    # 对于未在预期列表中的文件，提醒用户检查
    for filename in os.listdir(TARGET_FOLDER):
        if filename.endswith('.md') and filename not in EXPECTED_FILES:
            print(f"警告: 未处理的文件: {filename}，请手动检查其内容是否完整")
    
    print("文件恢复操作完成！")

if __name__ == '__main__':
    print("开始恢复文件内容...")
    restore_all_files()