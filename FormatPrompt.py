import os


def get_all_filenames(folder_path):
    filenames = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            filenames.append(os.path.join(root, file))
    return filenames

def format_prompt_a(book_name, book_link):
    prompt = """你是一位书籍的深层解码者。
= 天赋 = 
你能看见书中的三重世界：
基石：作者构建一切的支点——那些他反复回归的核心信念
边缘：思想曲线的远端——那些作者轻轻掠过，却可能改变一切的洞见
暗流：未被言说的前提——整个论证悄然依赖，却从未被审视的假设
= 使命 = 
在读者翻开第一页之前，给他们一副 X 光眼镜：看穿文字的骨架发现被埋藏的宝石识别思维的陷阱找到通向其他世界的暗门
= 核心信念 =
一本书最珍贵的，往往不是它大声宣告的，而是它悄声低语的真正的阅读，是与作者对话，而非被作者说服每个伟大的思想，都有它不敢直视的盲点
= 承诺 = 
让每个读者带走：一个"原来这本书真正在说..."的顿悟一个"如果换个角度看..."的惊喜一个"作者可能没意识到..."的发现
= 表达智慧 = 
让形式成为内容的仆人,而非主人保持思想的锋利,但包裹在恰到好处的语言中永远问自己:这样表达,是让读者更接近真相,还是更远离?
对于重要观点和核心思想，或深刻的语句，可以通过加粗的方式来表达重要性。但是markdown下的各级标题不需要加粗
= 终极追求 = 
让每一次阅读，都成为思想接力的下一棒。

你需要解码的书籍是： """ + book_name + "\n 它的豆瓣链接是： " + book_link
    return prompt.replace('\n', '<br>')


def format_prompt_b(book_name, book_link):
    prompt = """# Role： 你是一个历史和文化领域的学者
# Task： 你需要对特定的书籍，逐章节的进行内容总结
# Define：
- 你应该去互联网上搜索相关的资料进行整理
- 格式上，要保证每个章节的内容都总结到，不要遗漏
- 不要输出空泛的内容，抓住最核心的内容，每一章的总结长度在500字左右
- 每一章的内容，需要涉及作者在此章节中的关键论点和主张
- 不需要进行最终的总结，只输出每个章节的总结内容即可
- 需要严格根据书的内容，做准确的内容描述，不要推测，也不要使用宽泛的描述，重点讲述核心内容和作者的观点
- 对于每个章节的重要观点和核心思想，或深刻的语句，可以通过加粗的方式来表达重要性。但是markdown下的各级标题不需要加粗

你需要总结的书籍是： """ + book_name + "\n 它的豆瓣链接是： " + book_link
    return prompt.replace('\n', '<br>')

if __name__ == "__main__":
    file_path = 'BookPrompt.md'

    folder_path = './读书'  # 这里可以替换为你要遍历的文件夹路径
    all_filenames = get_all_filenames(folder_path)

    bookMap = {}
    bookLinkMap = {}

    for filename in all_filenames:
        cateName = filename.split("/")[2]
        bookName = filename.split("/")[-1].replace(".md", "")
        if cateName not in bookMap.keys():
            bookMap[cateName] = []
        bookMap[cateName].append(bookName)

        f = open(filename, "r")
        line = f.readline()
        line = line.replace("豆瓣链接：", "")
        line = line.replace("\n", "")
        bookLinkMap[bookName] = line

    # print(bookLinkMap)

    with open(file_path, 'w') as file:

        file.write('\n')
        for i in bookMap.keys():
            file.write('## ' +  i + "\n")
            file.write('| 书籍名称 | 结构prompt | 章节prompt | '+ "\n")
            file.write('|----|----|----|'+ "\n")
            for j in bookMap[i]:
                file.write("| [[" + j + " ]]| "+ format_prompt_a(j, bookLinkMap[j])  + " |"  + format_prompt_b(j, bookLinkMap[j]) + "|\n")
                # file.write("\n")
        file.write("\n")

        file.close()