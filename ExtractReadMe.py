import os


def get_all_filenames(folder_path):
    filenames = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            filenames.append(os.path.join(root, file))
    return filenames


if __name__ == "__main__":
    file_path = 'README.md'

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
        file.write('# 书籍类别统计：\n')
        file.write('| 书籍分类 | 数目|' + "\n")
        file.write('|----|----|' + "\n")
        for i in bookMap.keys():
            file.write('|' + i + " | " + str(len(bookMap[i])) + "本" + " |\n")
        file.write('\n')

        file.write('# 书籍目录明细：\n')
        file.write('\n')
        for i in bookMap.keys():
            file.write('## ' +  i + "\n")
            file.write('| 书籍名称 | 豆瓣链接|'+ "\n")
            file.write('|----|----|'+ "\n")
            for j in bookMap[i]:
                file.write("| [[" + j + " ]]| "+ bookLinkMap[j] + " |"  + "\n")
                # file.write("\n")
        file.write("\n")

        file.close()