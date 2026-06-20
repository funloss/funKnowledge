# 读书笔记库 - 项目记忆

## 已有 Skills

### book-notes-generator
- 位置：`~/.workbuddy/skills/book-notes-generator/`
- 功能：根据书名生成符合 Obsidian 知识库格式的深度读书笔记
- 触发词：生成读书笔记、写读书笔记、解读书籍、书籍笔记、读书卡片
- 输出格式：YAML 头部 + 可选 Mermaid 思维导图 + 深层解构（基石/边缘/暗流）+ 章节内容

### book-notes-enricher
- 功能：批量补充读书笔记 YAML 头部缺失的 tags 和 cover 字段
- 注意：依赖 Ollama 运行或 OPENAI_API_KEY

## 笔记格式规范
- YAML 头部字段：tags, douban_link, score, cover, create_time
- 深层解构 + 章节内容 两部分核心结构
- 非虚构类书籍建议加 Mermaid 思维导图
- 评分 1-5 分制
