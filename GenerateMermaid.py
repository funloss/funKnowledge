from openai import OpenAI
import os

def get_all_filenames(folder_path):
    filenames = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            filenames.append(os.path.join(root, file))
    return filenames

def callLLM(prompt):
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key="sk-11ec62a50c9a4862a1e490e6ea07fc54",  # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    completion = client.chat.completions.create(
        model="deepseek-r1",  # 此处以 deepseek-r1 为例，可按需更换模型名称。
        messages=[
            {'role': 'user', 'content': prompt}
        ]
    )

    # 通过reasoning_content字段打印思考过程
    # print("思考过程：")
    # print(completion.choices[0].message.reasoning_content)

    # 通过content字段打印最终答案
    result = completion.choices[0].message.content
    # print("最终答案：")
    # print(result)
    return result

file_path = 'Mermaid/chinese_history.md'

folder_path = './读书/中国历史'  # 这里可以替换为你要遍历的文件夹路径
all_filenames = get_all_filenames(folder_path)
# all_filenames = ['./读书/中国历史/邓小平时代.md']

bookMap = {}
bookLinkMap = {}

mermaid_file = open(file_path)
current_content = mermaid_file.read()
mermaid_file.close()

for filename in all_filenames:
    if str(filename) in current_content:
        print(filename + "is already draw, skip")
        continue

    try:
        f = open(filename, "r")
        line = f.read()
        f.close()

        print(filename)

        prompt = "我会在下面给你一段长文本，请根据文本的内容进行总结和格式化，我希望得到一个mermaid格式的思维导图（mindmap），能够对文本中的关键信息进行系统和结构化的梳理和呈现。\n"
        prompt += "你的导图设计导图既要保持对原著理论框架的尊重，又能通过边缘延伸和认知暗流的分支，呈现出解构性阅读的深度。要参考章节中的关键内容，但不能只是标题章节的简单罗列。每个节点控制在15字以内，符合思维导图的可视化原则。\n"
        prompt += "同时注意，不要使用 < > ├─ └─ \" 等符号\n"
        prompt += line

        # print(prompt)
        # break

        result = callLLM(prompt)

        with open(file_path, 'a') as file:
            file.write('\n')
            file.write('## ' + str(filename) + "\n")
            file.write(result)
            file.write("\n")
        file.close()

    except:
        with open(file_path, 'a') as file:
            file.write('\n')
            file.write('## ' + str(filename) + "\n")
            file.write('## ERROR \n')
            file.write("\n")
        file.close()
        continue


# print(bookLinkMap)