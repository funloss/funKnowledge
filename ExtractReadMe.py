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
    for filename in all_filenames:
        cateName = filename.split("/")[2]
        bookName = filename.split("/")[-1]
        if cateName not in bookMap.keys():
            bookMap[cateName] = []
        bookMap[cateName].append(bookName)

    print(bookMap)

    with open(file_path, 'w') as file:
        file.write('# 书籍目录\n')
        file.write('\n')
        for i in bookMap.keys():
            file.write('## ' +  i + "\n")
            for j in bookMap[i]:
                j = str.replace(j, ".md", "")
                file.write(j + "\n")
                file.write("\n")
        file.write("\n")

        file.close()