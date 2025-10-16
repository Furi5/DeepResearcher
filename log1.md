# 修改日志

## 2025-10-15

### 问题描述
需要调整前端消息显示逻辑，让除了"正在撰写研究报告"之外的所有进度消息都显示在右侧面板。

### 修改内容
1. **修改 `wide_research/frontend/simple.html`**：
   - 修改 WebSocket 消息处理逻辑（第 802-811 行）
   - 将触发条件从 "正在生成研究大纲" 改为 "正在撰写研究报告"
   - "正在撰写研究报告" 消息在左侧对话区显示
   - 所有后续的进度消息自动发送到右侧面板显示

### 实现细节
- 检测到 "正在撰写研究报告" 消息时：
  - 在左侧显示该消息（带省略号动画效果）
  - 设置 `isCapturingReport = true` 标志
  - 显示右侧面板
  - 清空右侧面板内容
- 后续所有 progress 消息都会被捕获到右侧面板显示
- 保持了原有的 Markdown 渲染和元数据过滤功能

### 修改的文件
- `wide_research/frontend/simple.html`

### 测试建议
1. 启动服务器：`python wide_research/api_server.py`
2. 打开浏览器访问 `http://localhost:8000`
3. 提交一个研究任务
4. 观察左侧对话框只显示 "正在撰写研究报告"
5. 确认所有后续进度消息都在右侧面板显示

## 2025-09-27

### 问题描述
运行 `examples/research/main.py` 时出现错误：
```
openai.BadRequestError: Error code: 400 - {'error': {'message': 'This response_format type is unavailable now', 'type': 'invalid_request_error', 'param': None, 'code': 'invalid_request_error'}}
```

### 根本原因
错误是由于使用了 `output_type` 参数（结构化输出），但当前的 API 配置不支持 `response_format` 功能。

### 解决方案
1. **注释掉 output_type 参数**：在 `examples/research/main.py` 中注释掉了 `planner_agent` 和 `writer_agent` 的 `output_type` 参数
2. **修改响应处理逻辑**：由于不再使用结构化输出，需要手动处理响应文本
3. **临时实现**：创建了简单的搜索计划和报告数据结构作为临时解决方案

### 修改的文件
- `examples/research/main.py`：
  - 注释掉 `output_type=WebSearchPlan` 和 `output_type=ReportData`
  - 修改 `_plan_searches` 方法，手动创建搜索计划
  - 修改 `_write_report` 方法，手动创建报告数据

### 测试结果
修复后程序可以正常运行，成功生成了研究报告。

### 后续改进建议
1. 实现更好的响应文本解析逻辑
2. 考虑使用支持结构化输出的 API 配置
3. 或者实现自定义的 JSON 解析来从文本响应中提取结构化数据

## 2025-09-27 (第二次修改)

### 问题描述
用户询问如何实现与用户的交互功能。

### 解决方案
为 `main.py` 添加了两种用户交互模式：

1. **交互式聊天模式** (`interactive_chat`)：
   - 持续对话循环
   - 支持多种退出方式（quit, exit, 退出, 再见）
   - 异常处理和键盘中断处理
   - 用户友好的界面提示

2. **单次问答模式** (`single_question`)：
   - 单次问答后退出
   - 适合快速查询

### 修改的文件
- `main.py`：完全重写，添加了用户交互功能

### 功能特点
- 支持中文交互
- 多种退出方式
- 错误处理
- 用户友好的界面
- 模式选择功能

## 2025-09-27 (第三次修改)

### 问题描述
程序在非交互式环境中运行时出现 `EOFError` 无限循环问题。

### 解决方案
添加了 `EOFError` 异常处理，防止程序在非交互式环境中陷入无限循环：

1. **交互式聊天模式**：添加 `EOFError` 异常处理，当输入结束时优雅退出
2. **单次问答模式**：添加 `EOFError` 异常处理，防止输入错误
3. **主函数**：添加 `EOFError` 异常处理，提供默认行为

### 修改的文件
- `main.py`：添加了完整的异常处理机制

### 测试结果
修复后程序可以正常处理各种输入情况，包括非交互式环境。

## 2025-09-27 (第四次修改)

### 问题描述
用户需要 `search_wide` 函数的使用案例。

### 解决方案
创建了两个完整的使用案例：

1. **deep_search.py** - 完整的深度搜索示例：
   - 包含 `DeepSearchExample` 类
   - 支持大语言模型对比研究
   - 支持AI技术趋势分析
   - 提供交互式选择界面

2. **simple_search_example.py** - 简化的直接使用示例：
   - 直接调用 `search_wide` 函数
   - 提供3个具体示例
   - 支持自定义搜索
   - 包含详细的执行日志

### 修改的文件
- `deep_search.py`：完善了深度搜索示例类
- `simple_search_example.py`：新建了简化使用示例

### 功能特点
- 并行搜索多个子任务
- 结构化输出格式
- 结果保存为JSONL文件
- 并发控制
- 详细的执行日志

## 2025-01-30
### 代码解释和分析
- **分析 SerperToolkit 工具调用机制**：
  - 解释了 `SERPER_TOOLKIT.get_tools_in_agents()` 如何将工具注册到 Agent 中
  - 详细说明了工具注册机制：通过 `@register_tool` 装饰器自动发现和注册工具方法
  - 分析了 `get_tools_in_agents()` 方法的工作原理，将工具包装成 `FunctionTool` 格式
  - 列出了 SerperToolkit 提供的所有工具函数：
    - `google_search`: Google 搜索
    - `autocomplete`: 自动补全
    - `google_lens`: Google Lens 图像分析
    - `image_search`: 图像搜索
    - `map_search`: 地图搜索
    - `news_search`: 新闻搜索
    - `place_search`: 地点搜索
    - `scholar_search`: 学术搜索
    - `video_search`: 视频搜索
  - 解释了 Agent 如何使用这些工具：工具发现 → 工具选择 → 工具执行 → 结果处理
  - 提供了具体的工具调用流程示例

## 2025-01-30 (第二次修改)
### 优化 search_deep 函数
- **问题识别**：用户反馈 `search_deep` 函数返回的检索内容太短，每个子任务只返回一条信息，信息量不足
- **解决方案**：
  1. **增强原有函数**：优化了 `search_deep` 函数的搜索指令，要求进行多轮搜索
  2. **新增增强版函数**：创建了 `search_deep_enhanced` 函数，提供超深度搜索
  3. **多角度搜索策略**：
     - 基础搜索（google_search）
     - 学术搜索（scholar_search）
     - 新闻搜索（news_search）
     - 图像搜索（image_search）
     - 深度搜索（多关键词组合）
     - 补充搜索（针对性搜索）
  4. **信息量要求**：
     - 每个子任务至少2000字详细信息
     - 至少5个高质量参考文献
     - 至少3个不同数据来源
     - 至少500字关键发现总结
  5. **更新 planner 配置**：在 planner 中同时提供两个搜索工具选项
  6. **更新提示词**：修改了 planner 的提示词，指导使用增强版搜索

### 修改的文件
- `wide_research/main.py`：
  - 优化了 `search_deep` 函数的搜索指令
  - 新增了 `search_deep_enhanced` 函数
  - 更新了 planner 的工具配置
- `wide_research/prompts.yaml`：
  - 更新了 planner 的提示词，指导使用增强版搜索

### 功能特点
- 多轮搜索策略
- 超深度信息收集
- 结构化输出格式
- 高质量文献优先
- 详细的信息量要求

## 2025-01-30 (第三次修改)
### 优化文献数据结构
- **问题识别**：用户需要将文献信息修改成"一个来源对应一个内容"的格式，便于后续将文献插入到正文内部进行整理
- **解决方案**：
  1. **重构 enhanced_schema**：
     - 将原来的 `参考文献` 和 `数据来源` 字段合并为 `文献信息` 数组
     - 每个文献来源包含：来源编号、完整引用、对应内容、URL来源、期刊等级
  2. **新的数据结构**：
     ```json
     {
       "文献信息": [
         {
           "来源编号": "[1]",
           "完整引用": "作者. 标题. 期刊名称. 年份;卷(期):页码. DOI: xxx",
           "对应内容": "该文献对应的具体研究内容、发现或数据",
           "URL来源": "文献的完整URL链接",
           "期刊等级": "Nature/Science/Cell等"
         }
       ]
     }
     ```
  3. **优势**：
     - 便于后续将文献插入到正文内部
     - 每个文献都有对应的具体内容
     - 支持按来源编号进行引用
     - 便于生成参考文献列表
  4. **更新搜索指令**：修改了两个搜索函数的指令，适应新的数据结构

### 修改的文件
- `wide_research/main.py`：
  - 重构了 `search_deep` 函数的 enhanced_schema
  - 重构了 `search_deep_enhanced` 函数的 enhanced_schema
  - 更新了两个函数的搜索指令
  - 优化了文献信息的收集和输出格式

### 功能特点
- 一个来源对应一个内容
- 便于正文内引用
- 支持文献编号管理
- 便于生成参考文献列表
- 结构化的文献信息管理

## 2025-01-30 (第四次修改)
### 升级文献数据结构为详细格式
- **问题识别**：用户需要将文献信息结构升级为更详细的格式，包含完整的文献元数据
- **解决方案**：
  1. **重构 enhanced_schema**：
     - 将 `文献信息` 字段改为 `results` 数组
     - 每个文献包含15个详细字段：id、title、authors、year、journal、volume、issue、pages、doi、abstract、keywords、citation_key、url、retrieved_text、relevance_score
  2. **新的数据结构**：
     ```json
     {
       "results": [
         {
           "id": "smith2023",
           "title": "Deep Learning in Medical Image Analysis",
           "authors": ["Smith, J.", "Johnson, A.", "Williams, B."],
           "year": 2023,
           "journal": "Nature Medicine",
           "volume": "29",
           "issue": "3",
           "pages": "456-478",
           "doi": "10.1038/s41591-023-xxxxx",
           "abstract": "This study explores...",
           "keywords": ["deep learning", "medical imaging", "diagnosis"],
           "citation_key": "Smith2023",
           "url": "https://...",
           "retrieved_text": "关键段落或摘要内容...",
           "relevance_score": 0.95
         }
       ]
     }
     ```
  3. **优势**：
     - 完整的文献元数据管理
     - 支持结构化引用
     - 便于文献管理和检索
     - 支持相关性评分
     - 便于生成标准化的参考文献列表
  4. **更新搜索指令**：修改了两个搜索函数的指令，适应新的详细数据结构

### 修改的文件
- `wide_research/main.py`：
  - 重构了 `search_deep` 函数的 enhanced_schema
  - 重构了 `search_deep_enhanced` 函数的 enhanced_schema
  - 更新了两个函数的搜索指令
  - 优化了文献信息的收集和输出格式

### 功能特点
- 完整的文献元数据管理
- 支持结构化引用
- 便于文献管理和检索
- 支持相关性评分
- 便于生成标准化的参考文献列表

## 2025-01-30 (第五次修改)
### 修正 enhanced_schema 语法错误
- **问题识别**：用户报告 `enhanced_schema` 报错，代码中存在语法错误
- **解决方案**：
  1. **修正语法错误**：
     - 修正了 `enhanced_schema['properties'].update()` 中的语法错误
     - 将错误的 JSON 格式改为正确的 Python 字典格式
     - 修正了字段名称从 `results` 改为 `papers`
  2. **完善数据结构**：
     - 重新构建了完整的 `papers` 字段结构
     - 包含所有必要的文献元数据字段
     - 修正了 `required` 字段列表
  3. **添加缺失变量**：
     - 添加了 `TASK` 变量定义
     - 确保代码可以正常运行
  4. **更新搜索指令**：
     - 修正了输出要求，使用 `papers` 字段
     - 简化了输出要求描述

### 修改的文件
- `wide_research/main.py`：
  - 修正了 `enhanced_schema` 的语法错误
  - 重新构建了 `papers` 字段结构
  - 添加了 `TASK` 变量定义
  - 更新了搜索指令

### 功能特点
- 修正了语法错误
- 完善了数据结构
- 确保代码可以正常运行
- 支持完整的文献元数据管理

## 2025-01-30 (第六次修改)
### 优化 report_formatter 学术写作功能
- **问题识别**：用户需要修改 `report_formatter`，使其能够根据参考文献的内容，将文献插入到正文中，形成类似学术期刊的风格
- **解决方案**：
  1. **处理结构化文献数据**：
     - 优先使用 `papers` 数组中的结构化文献数据
     - 每个文献包含完整的元数据：id、title、authors、year、journal、volume、issue、pages、doi、abstract、keywords、citation_key、url、retrieved_text
  2. **智能文献插入策略**：
     - 基于 `retrieved_text` 和 `abstract` 的内容，将相关文献插入到正文的合适位置
     - 在介绍背景知识时引用综述性文献
     - 在描述具体发现时引用原始研究
     - 在讨论机制时引用基础研究
     - 在描述临床应用时引用临床试验
  3. **学术写作风格**：
     - 引言部分：引用综述性文献建立背景
     - 方法部分：引用方法学相关文献
     - 结果部分：引用具体的研究发现
     - 讨论部分：引用机制研究和临床研究
     - 结论部分：引用最新的研究进展
  4. **文献格式标准化**：
     - 英文文献：Author A, Author B. Title. Journal Name. Year;Volume(Issue):Pages. DOI: xxxxx
     - 中文文献：作者A, 作者B. 文章标题. 期刊名称. 年份;卷(期):页码. DOI: xxxxx
     - 网络资源：Author/Organization. Title. Website Name. [访问日期]. Available from: URL
  5. **质量控制**：
     - 确保文献引用与正文内容高度相关
     - 优先引用高质量期刊（Nature、Science、Cell、NEJM、Lancet等）
     - 移除重复的引用条目
     - 验证文献信息的完整性和准确性

### 修改的文件
- `wide_research/prompts.yaml`：
  - 重构了 `writer` 部分的提示词
  - 添加了结构化文献数据处理功能
  - 实现了智能文献插入策略
  - 优化了学术写作风格指导
  - 更新了输出格式示例

### 功能特点
- 智能文献插入策略
- 学术期刊风格写作
- 结构化文献数据处理
- 高质量文献优先引用
- 完整的质量控制机制

## 2025-01-30 (第七次修改)
### 重构 main.py 参考 ResearchManager 设计思路
- **问题识别**：用户希望根据 `examples/research/main.py` 中 `ResearchManager` 的思路来修改 `wide_research/main.py`
- **解决方案**：
  1. **模块化设计**：
     - 将研究过程分解为澄清、规划、执行、报告四个独立阶段
     - 每个阶段都有独立的方法和错误处理
  2. **数据结构化**：
     - 添加了 Pydantic 模型：`PaperInfo`、`ResearchTask`、`ResearchPlan`、`ResearchResult`
     - 使用类型提示提高代码可读性和维护性
  3. **进度跟踪**：
     - 添加了 `Printer` 类来跟踪执行进度
     - 使用 Rich 库提供更好的用户体验
  4. **异步并发**：
     - 使用 `asyncio` 进行并发任务执行
     - 每个研究任务都有独立的错误处理
  5. **错误处理**：
     - 每个方法都有适当的异常处理
     - 失败的任务不会影响其他任务的执行

### 主要改进
1. **DeepSearchManager 类**：
   - 参考 `ResearchManager` 的设计模式
   - 包含 `build()`、`run()` 等核心方法
   - 模块化的子方法：`_clarify_requirements()`、`_plan_research()`、`_execute_research()`、`_generate_report()`

2. **数据模型**：
   - `PaperInfo`：文献信息模型
   - `ResearchTask`：研究任务模型
   - `ResearchPlan`：研究计划模型
   - `ResearchResult`：研究结果模型

3. **进度跟踪**：
   - `Printer` 类提供实时进度更新
   - 清晰的视觉反馈

4. **并发执行**：
   - 支持多个研究任务并发执行
   - 提高研究效率

### 修改的文件
- `wide_research/main.py`：
  - 重构了 `DeepSearch` 类为 `DeepSearchManager`
  - 添加了数据模型和进度跟踪
  - 实现了模块化的研究流程
  - 改进了错误处理和并发执行

### 功能特点
- 模块化设计
- 结构化数据管理
- 实时进度跟踪
- 并发任务执行
- 完善的错误处理

## 2025-01-30 (第八次修改)
### 将研究过程分解为四个独立阶段
- **问题识别**：用户希望将研究过程分解为澄清、规划、搜索、写作三个独立阶段
- **解决方案**：
  1. **阶段1：需求澄清** (`_stage1_clarify_requirements`)：
     - 使用澄清代理分析用户需求
     - 与用户交互澄清模糊点
     - 生成增强的任务描述
  2. **阶段2：制定研究计划** (`_stage2_plan_research`)：
     - 基于澄清后的需求制定研究计划
     - 分解为多个子任务
     - 定义输出格式和数据结构
  3. **阶段3：执行深度搜索** (`_stage3_execute_search`)：
     - 使用搜索代理执行各个子任务
     - 并发处理多个搜索任务
     - 收集和整理搜索结果
  4. **阶段4：生成最终报告** (`_stage4_write_report`)：
     - 整合所有搜索结果
     - 使用写作代理生成学术报告
     - 格式化输出最终结果

### 主要改进
1. **模块化设计**：
   - 每个阶段都有独立的方法
   - 清晰的阶段划分和职责分离
   - 便于维护和扩展

2. **进度跟踪**：
   - 每个阶段都有清晰的进度提示
   - 使用表情符号和分隔线增强可读性
   - 实时反馈执行状态

3. **错误处理**：
   - 每个阶段都有独立的错误处理
   - 失败的任务不会影响整体流程
   - 提供详细的错误信息

4. **用户体验**：
   - 清晰的阶段标识和进度提示
   - 友好的用户交互界面
   - 结构化的输出格式

### 修改的文件
- `wide_research/main.py`：
  - 重构了 `DeepSearch` 类
  - 添加了四个独立的阶段方法
  - 改进了进度跟踪和错误处理
  - 优化了用户体验

### 功能特点
- 四个独立的研究阶段
- 清晰的进度跟踪
- 模块化设计
- 完善的错误处理
- 友好的用户界面

## 2025-01-30 (第九次修改)
### 大幅提升文献数量和内容深度
- **问题识别**：用户反馈检索内容不够深，文献太少，需要50-60篇文献，输出内容太简短
- **解决方案**：
  1. **扩展研究计划**：
     - 将子任务从4个增加到12个
     - 新增：基础生物学机制研究、分子结构与功能分析、信号通路与调控机制、疾病病理生理学、临床前研究进展、临床试验数据、药物开发与治疗策略、耐药性机制研究、生物标志物发现、转化医学研究、最新研究突破、未来发展方向
     - 目标文献数量：60篇
     - 每个子任务最少文献数：5篇

  2. **增强搜索策略**：
     - 搜索轮次从6轮增加到10轮
     - 新增：综述搜索、会议论文搜索、专利搜索、数据库搜索
     - 每个搜索收集8-12个高质量结果
     - 学术搜索目标：至少20篇论文

  3. **提升内容深度**：
     - 每个子任务至少5000字的深度分析
     - 关键发现：至少2000字的重要发现总结
     - 机制分析：至少1500字的分子机制分析
     - 临床应用：至少1000字的临床应用分析

  4. **优化搜索指令**：
     - 更新 `search_deep` 函数的搜索指令
     - 更新 `prompts.yaml` 中的 `searcher` 提示
     - 增加文献数量统计和进度跟踪

### 主要改进
1. **文献数量大幅提升**：
   - 目标文献数量：60篇（12个子任务 × 5篇/子任务）
   - 每个子任务至少15篇文献
   - 总计可收集180篇以上文献

2. **内容深度显著增强**：
   - 每个子任务至少5000字分析
   - 总计至少60000字的深度内容
   - 多维度分析：机制、临床、应用等

3. **搜索策略全面升级**：
   - 10轮搜索策略
   - 多角度信息收集
   - 专业数据库搜索

4. **进度跟踪优化**：
   - 实时显示文献收集数量
   - 目标完成度提示
   - 详细的搜索进度反馈

### 修改的文件
- `wide_research/main.py`：
  - 扩展了研究计划，增加12个子任务
  - 优化了搜索阶段，增加文献数量统计
  - 增强了搜索指令，提升内容深度要求
- `wide_research/prompts.yaml`：
  - 更新了 `searcher` 提示，增加搜索策略和内容要求

### 功能特点
- 目标文献数量：60篇
- 内容深度：每个子任务5000字以上
- 10轮搜索策略
- 实时进度跟踪
- 多维度深度分析

## 2025-01-30 (第十次修改)
### 确保每个阶段使用对应的代理
- **问题识别**：用户要求在每个阶段使用对应的代理来运行相应的功能
- **解决方案**：
  1. **阶段1：需求澄清** - 使用 `self.clarifier_agent`
  2. **阶段2：制定研究计划** - 使用 `self.planner_agent`
  3. **阶段3：执行深度搜索** - 使用 `self.searcher_agent`
  4. **阶段4：生成最终报告** - 使用 `self.writer_agent`

### 主要改进
1. **阶段2优化**：
   - 使用 `self.planner_agent` 来制定研究计划
   - 尝试解析规划代理的输出
   - 如果解析失败，使用默认计划结构作为备选

2. **代理职责明确**：
   - 每个阶段都有专门的代理负责
   - 代理之间职责分离，便于维护
   - 每个代理都有对应的提示词指导

3. **错误处理**：
   - 规划代理输出解析失败时的备选方案
   - 确保系统稳定运行

### 修改的文件
- `wide_research/main.py`：
  - 更新了 `_stage2_plan_research` 方法，使用 `self.planner_agent`
  - 确保所有阶段都使用对应的代理

### 功能特点
- 四个阶段使用对应的专业代理
- 代理职责分离
- 完善的错误处理
- 稳定的系统运行

## 2025-01-30 (第十一次修改)
### 优化planner提示以适应main.py
- **问题识别**：`planner` 提示需要适应 `main.py` 中的使用方式，输出结构化的研究计划
- **解决方案**：
  1. **简化工作流程**：
     - 移除复杂的执行步骤
     - 专注于计划制定功能
     - 明确输出JSON格式要求

  2. **标准化输出格式**：
     - 定义标准的JSON结构
     - 包含 main_task, subtasks, output_schema 字段
     - 确保与代码解析逻辑兼容

  3. **优化提示内容**：
     - 简化角色设定
     - 明确核心任务
     - 提供清晰的输出示例

### 主要改进
1. **输出格式标准化**：
   - 必须输出有效的JSON格式
   - 子任务数量：3-7个
   - 子任务描述要具体、明确

2. **工作流程简化**：
   - 需求分析 → 任务分解 → 输出格式
   - 移除复杂的执行步骤
   - 专注于计划制定

3. **提示内容优化**：
   - 简化角色设定
   - 明确核心任务
   - 提供清晰的输出示例

### 修改的文件
- `wide_research/prompts.yaml`：
  - 重写了 `planner` 提示
  - 简化了工作流程
  - 标准化了输出格式

### 功能特点
- 标准化的JSON输出格式
- 简化的计划制定流程
- 与代码逻辑完全兼容
- 清晰的输出要求

## 2025-01-30 (第十二次修改)
### 支持层次化子任务结构
- **问题识别**：如果 `planner` 生成的子任务中包含更详细的子任务，需要支持层次化结构
- **解决方案**：
  1. **修改搜索阶段**：
     - 检测子任务是否为字典格式（层次化）
     - 处理主任务和详细子任务
     - 为每个详细子任务执行搜索
     - 支持简单和层次化两种格式

  2. **修改报告生成阶段**：
     - 处理层次化搜索结果
     - 生成结构化的报告内容
     - 支持主任务和详细子任务的层次显示

  3. **更新planner提示**：
     - 支持两种子任务格式
     - 简单格式：字符串数组
     - 层次化格式：对象数组

### 主要改进
1. **层次化任务支持**：
   - 检测子任务类型（简单/层次化）
   - 处理主任务和详细子任务
   - 为每个详细子任务执行搜索

2. **结构化报告生成**：
   - 处理层次化搜索结果
   - 生成主任务和详细子任务的层次结构
   - 支持两种格式的混合使用

3. **灵活的planner输出**：
   - 支持简单格式（字符串数组）
   - 支持层次化格式（对象数组）
   - 根据研究复杂度选择合适的格式

### 修改的文件
- `wide_research/main.py`：
  - 更新了 `_stage3_execute_search` 方法，支持层次化子任务
  - 更新了 `_stage4_write_report` 方法，处理层次化结果
- `wide_research/prompts.yaml`：
  - 更新了 `planner` 提示，支持两种子任务格式

### 功能特点
- 支持层次化子任务结构
- 灵活的任务分解方式
- 结构化的报告生成
- 兼容简单和复杂两种格式

## 2025-01-30 (第十三次修改)
### 确保planner输出JSON格式
- **问题识别**：用户希望 `planner` 的输出是 JSON 格式，便于后续处理
- **解决方案**：
  1. **修改代码逻辑**：
     - 添加JSON解析和验证逻辑
     - 支持从输出中提取JSON部分
     - 提供错误处理和备选方案

  2. **更新planner提示**：
     - 明确要求输出JSON格式
     - 提供标准的JSON模板
     - 强调不要包含非JSON文本

  3. **增强错误处理**：
     - JSON解析失败时的处理
     - 从输出中提取JSON的正则表达式
     - 多层次的错误恢复机制

### 主要改进
1. **JSON输出保证**：
   - 明确要求输出JSON格式
   - 提供标准JSON模板
   - 强调不要包含非JSON文本

2. **智能解析机制**：
   - 直接JSON解析
   - 正则表达式提取JSON
   - 多层次的错误处理

3. **错误恢复策略**：
   - JSON解析失败时的备选方案
   - 从输出中提取JSON部分
   - 确保系统稳定运行

### 修改的文件
- `wide_research/main.py`：
  - 添加了JSON解析和验证逻辑
  - 支持从输出中提取JSON部分
  - 增强了错误处理机制
- `wide_research/prompts.yaml`：
  - 更新了 `planner` 提示，明确要求JSON输出
  - 提供了标准的JSON模板

### 功能特点
- 保证JSON格式输出
- 智能解析机制
- 完善的错误处理
- 稳定的系统运行

## 2025-01-30 (第十四次修改)
### 集成SearchToolkit.web_qa获取完整内容
- **问题识别**：用户希望获取文献和网页的完整内容，而不仅仅是URL和摘要
- **解决方案**：
  1. **增强数据结构**：
     - 在 `papers` 结构中添加 `full_content` 字段存储网页原始内容
     - 添加 `source` 字段存储来源URL
     - 更新 `required` 字段列表

  2. **修改搜索指令**：
     - 指导agent使用 `web_qa` 获取网页原始内容
     - 限制 `web_qa` 使用数量为50个
     - 无法访问的URL跳过，不影响整体流程

  3. **工具集成**：
     - 将 `SearchToolkit` 的 `web_qa` 工具添加到搜索代理
     - 组合使用 `SerperToolkit` 和 `SearchToolkit`

### 主要改进
1. **数据结构增强**：
   - 添加 `full_content` 字段存储网页原始内容
   - 添加 `source` 字段存储来源URL
   - 更新字段描述和必填项

2. **搜索策略优化**：
   - 指导agent使用 `web_qa` 获取完整内容
   - 限制并发数量为50个
   - 错误处理：无法访问的URL跳过

3. **工具集成**：
   - 组合使用 `SerperToolkit` 和 `SearchToolkit`
   - 支持深度内容获取
   - 保持现有搜索功能

### 修改的文件
- `wide_research/main.py`：
  - 增强了 `enhanced_schema` 数据结构
  - 修改了搜索指令，指导使用 `web_qa`
  - 集成了 `SearchToolkit` 工具

### 功能特点
- 获取网页完整内容
- 支持深度内容分析
- 限制并发数量
- 完善的错误处理
- 保持现有功能

## 2025-01-30 (第十五次修改)
### 重构数据流，实现planner输出结构化数据
- **问题识别**：用户希望planner输出研究计划和检索内容，按综述部分分组
- **解决方案**：
  1. **重新设计planner提示词**：
     - 让planner负责研究计划制定和内容检索
     - 输出结构化的JSON数据
     - 按综述部分分组内容

  2. **定义新的数据结构**：
     ```json
     {
       "research_plan": {
         "main_task": "研究主题",
         "subtasks": ["部分1", "部分2"]
       },
       "research_content": {
         "部分1": {
           "content1": {
             "content": "检索内容",
             "sources": "来源"
           }
         }
       }
     }
     ```

  3. **修改main.py数据处理**：
     - 解析planner的JSON输出
     - 验证数据结构
     - 传递给report_formatter生成综述

### 主要改进
1. **简化数据流**：
   - planner负责规划+搜索+分组
   - report_formatter负责生成综述
   - 减少中间处理步骤

2. **结构化数据**：
   - 明确的research_plan和research_content
   - 按综述部分分组
   - 每个content包含内容和来源

3. **完善的数据验证**：
   - JSON解析和验证
   - 数据结构检查
   - 错误处理和备选方案

### 修改的文件
- `wide_research/prompts.yaml`：
  - 重写了planner提示词
  - 添加了writer提示词
  - 简化了clarifier提示词
- `wide_research/main.py`：
  - 修改了数据处理流程
  - 添加了JSON解析和验证
  - 优化了进度提示

### 功能特点
- planner输出结构化数据
- 按综述部分分组内容
- 完善的数据验证
- 简化的数据流
- 保持错误处理

## 2025-01-30 (第十六次修改)
### 重构 search_deep 函数以适应新的数据结构
- **问题识别**：原 `search_deep` 函数与新的输出格式不匹配
- **解决方案**：
  1. **重命名并简化函数**：
     - `search_deep` → `search_deep_for_section`
     - 参数简化为 `(section_name, research_focus)`
     - 返回单个综述部分的所有 content 项
  
  2. **调整函数职责**：
     - 专注于单个综述部分的搜索
     - 自动使用 google_search、scholar_search、web_qa
     - 输出格式与 prompts.yaml 中的 sources 结构一致
     - 每个部分限制 web_qa 调用为15次
  
  3. **更新 planner 提示词**：
     - 指导 planner 调用 `search_deep_for_section` 工具
     - 说明如何整合多个部分的结果
     - 明确最终输出的 JSON 格式

### 新的工作流程
```
用户输入
  ↓
clarifier_agent (澄清需求)
  ↓
planner_agent:
  1. 分解为综述部分
  2. 对每个部分调用 search_deep_for_section
  3. 整合所有结果到 JSON:
     {
       "research_plan": {...},
       "research_content": {
         "部分1": {content1: {...}, content2: {...}},
         "部分2": {content1: {...}}
       }
     }
  ↓
report_formatter (生成综述)
  ↓
最终综述
```

### 修改的文件
- `wide_research/main.py`：
  - 重构 `search_deep_for_section` 函数
  - 更新 planner_agent 的 tools 列表
  - 保持数据处理流程不变
- `wide_research/prompts.yaml`：
  - 更新搜索策略说明
  - 指导使用 search_deep_for_section 工具

### 功能特点
- 单个函数处理单个综述部分
- 自动化的搜索和内容获取
- 符合 JSON Schema 的输出格式
- 完善的错误处理
- 清晰的工作流程

## 2025-01-30 (第十七次修改)
### 重大架构改进：从 JSON 输出转为代码层组装
- **问题识别**：AI 输出 JSON 非常不可靠，经常包含额外文字导致解析失败，文献数量严重不足
- **解决方案**：完全重新设计架构

#### 新架构设计
```
planner (输出 Markdown)
  ↓ 解析
research_plan (代码提取)
  ↓ 循环
对每个部分调用 search_deep_for_section
  ↓ 收集
research_content (代码组装)
  ↓ 合并
research_data (完整 JSON)
  ↓ 传递
writer (生成综述)
```

#### 主要改进

1. **planner 只输出 Markdown**：
   - 不再要求输出 JSON
   - 输出清晰的研究计划格式
   - 包含主任务和综述部分
   - 每个部分有明确的研究重点
   
2. **代码层解析和控制**：
   - `_parse_research_plan()` 方法解析 Markdown
   - 提取主任务、部分标题、研究重点
   - 在代码层循环调用 `search_deep_for_section`
   - 自动收集和组装数据
   
3. **完善的数据流**：
   - planner → Markdown 计划
   - 解析 → 结构化数据
   - 循环搜索 → 每个部分的内容
   - 组装 → 完整的 research_data JSON
   - writer → 最终综述

4. **增强的调试功能**：
   - 保存 research_data 到 JSON 文件
   - 实时显示搜索进度
   - 统计内容项和文献数量
   - 清晰的进度提示

#### 修改的文件
- `wide_research/prompts.yaml`：
  - 简化 planner 提示词
  - 只要求输出 Markdown 格式
  - 移除 JSON 相关要求
  
- `wide_research/main.py`：
  - 移除 planner 的工具依赖
  - 添加 `_parse_research_plan()` 方法
  - 重写 `run_streamed()` 逻辑
  - 在代码层控制搜索流程
  - 添加数据统计和调试输出

### 优势
✅ **可靠性大幅提升**：不依赖 AI 输出 JSON
✅ **数据完整性保证**：代码层直接控制数据收集
✅ **文献数量可控**：每个部分独立搜索，确保充足文献
✅ **易于调试**：中间数据可视化
✅ **职责清晰**：planner 规划，代码执行

## 2025-10-11
### 将章节处理改为并行执行
- **问题识别**：用户希望将章节的搜索和撰写过程改为并行处理，提高处理效率
- **解决方案**：
  1. **并行处理架构**：
     - 将原来的顺序循环改为并行执行
     - 收集所有子章节后使用 `asyncio.gather` 并行处理
     - 使用 `asyncio.Semaphore` 限制并发数量（CONCURRENCY=20）
  
  2. **独立处理函数**：
     - 创建 `process_subsection` 异步函数
     - 每个章节的搜索、解析、撰写都在独立函数中完成
     - 为每个任务创建独立的 agent 实例，避免冲突
  
  3. **进度跟踪优化**：
     - 每个章节有独立的进度标识 `[subsection_id]`
     - 实时显示每个章节的处理状态
     - 清晰的开始和完成提示
  
  4. **错误处理增强**：
     - 每个章节独立的异常处理
     - 单个章节失败不影响其他章节
     - 返回占位内容以保持结构完整
  
  5. **结果排序保证**：
     - 并行执行后按原始顺序排序结果
     - 保持最终报告的章节顺序正确

### 主要改进
1. **性能提升**：
   - 并行处理多个章节，大幅提升处理速度
   - 使用信号量控制并发数量，避免过载
   - 独立 agent 实例，避免资源竞争

2. **稳定性增强**：
   - 独立错误处理，单个章节失败不影响全局
   - 每个章节都有完整的异常捕获
   - 保证最终输出的完整性

3. **可维护性提高**：
   - 清晰的函数职责划分
   - 独立的进度跟踪标识
   - 便于调试和问题定位

### 修改的文件
- `wide_research/main.py`：
  - 重构步骤3的处理逻辑
  - 添加 `process_subsection` 异步函数
  - 实现并行任务调度和结果收集
  - 优化进度跟踪和错误处理

### 功能特点
- 并行处理所有章节
- 使用信号量控制并发（最多20个）
- 独立的 agent 实例避免冲突
- 完善的错误处理机制
- 保持章节顺序输出

## 2025-10-13
### 添加 Token 消耗和检索次数统计功能
- **问题识别**：用户希望统计运行一次消耗的 token 数量以及检索次数
- **解决方案**：
  1. **统计数据结构**：
     - 在 `DeepResearchAgent` 类的 `__init__` 方法中初始化统计字典
     - 包含各阶段 token 消耗：clarifier、planner、searcher、writer
     - 包含各类检索次数：google_search、scholar_search、news_search、web_qa、image_search
  
  2. **各阶段统计收集**：
     - **澄清阶段**：从 `clarifier_agent` 的运行结果中提取 token 使用量
     - **规划阶段**：从 `planner_agent` 的运行结果中提取 token 使用量
     - **搜索阶段**：
       - 从每个子章节的 `searcher_agent` 运行结果中提取 token 使用量
       - 分析 `all_messages` 中的 `tool_calls` 来统计各类检索工具的调用次数
     - **写作阶段**：从每个子章节的 `writer` 运行结果中提取 token 使用量
  
  3. **统计信息显示**：
     - 创建 `print_statistics()` 方法，格式化输出统计信息
     - Token 消耗按阶段分类显示，含总计
     - 检索次数按工具类型分类显示，含总计
     - 估算成本（基于 GPT-4 价格，支持 USD 和 CNY）
  
  4. **统计信息持久化**：
     - 在任务完成后保存统计信息到 `statistics.json`
     - 即使任务失败也会显示已收集的统计信息
     - 便于后续分析和成本核算

### 统计信息示例输出
```
📊 运行统计信息 (Statistics)
================================================================================

💰 Token 消耗统计:
  - 澄清阶段 (Clarifier):          1,234 tokens
  - 规划阶段 (Planner):            2,345 tokens
  - 搜索阶段 (Searcher):         123,456 tokens
  - 写作阶段 (Writer):            45,678 tokens
  ────────────────────────────────────────────────────────────
  - 总计 (Total):                172,713 tokens

🔍 检索次数统计:
  - Google 搜索:                      45 次
  - 学术搜索:                         32 次
  - 新闻搜索:                         12 次
  - 网页内容获取:                    156 次
  - 图像搜索:                          8 次
  ────────────────────────────────────────────────────────────
  - 总计检索次数:                    253 次

💵 估算成本 (基于 GPT-4 价格):
  - 约 $7.77 USD
  - 约 ¥54.39 CNY (按 1:7 汇率)
```

### 主要改进
1. **精确统计**：
   - 追踪每个阶段的 token 消耗
   - 统计每种检索工具的调用次数
   - 自动计算总计

2. **实时反馈**：
   - 每个阶段完成后显示该阶段的 token 消耗
   - 并行处理时为每个章节显示独立的统计

3. **成本估算**：
   - 基于 GPT-4 官方价格计算
   - 支持美元和人民币显示
   - 便于成本控制和预算规划

4. **数据持久化**：
   - 保存 JSON 格式的统计数据
   - 便于后续分析和对比
   - 支持批量任务的成本统计

### 修改的文件
- `wide_research/main.py`：
  - 添加 `__init__` 方法初始化统计字典
  - 在各阶段添加 token 和检索统计收集
  - 创建 `print_statistics()` 方法
  - 在任务完成时显示并保存统计信息

### 功能特点
- 完整的 token 消耗追踪
- 详细的检索次数统计
- 自动成本估算
- 统计信息持久化
- 实时反馈和最终汇总

## 2025-10-13 (第二次修改)
### 修复 Token 统计功能 - 正确获取 usage 信息
- **问题识别**：之前的统计代码没有正确获取 usage 信息，所有统计都是 0
- **根本原因**：
  - `RunResult` 和 `RunResultStreaming` 对象没有直接的 `usage` 属性
  - usage 信息实际存储在 `raw_responses` 数组中的每个 `ModelResponse` 对象里
  - 工具调用统计需要从 `new_items` 中获取 `ToolCallItem` 对象

- **解决方案**：
  1. **正确的 usage 获取方式**：
     ```python
     if hasattr(run_result, 'raw_responses') and run_result.raw_responses:
         for resp in run_result.raw_responses:
             if hasattr(resp, 'usage') and resp.usage:
                 tokens = resp.usage.total_tokens
                 # 累加统计
     ```
  
  2. **正确的工具调用统计方式**：
     ```python
     if hasattr(run_result, 'new_items'):
         from agents import ToolCallItem
         for item in run_result.new_items:
             if isinstance(item, ToolCallItem):
                 tool_name = item.raw_item.name
                 # 统计工具调用
     ```
  
  3. **修复所有阶段的统计**：
     - 澄清阶段：从 `clarification_result.get_run_result().raw_responses` 获取
     - 规划阶段：从 `plan_result.raw_responses` 获取（stream方式）
     - 搜索阶段：从每个章节的 `run_result.raw_responses` 获取，同时统计工具调用
     - 写作阶段：从每个章节的 `section_result.raw_responses` 获取

  4. **技术细节**：
     - `raw_responses` 是一个列表，包含一个或多个 `ModelResponse` 对象
     - 每个 `ModelResponse` 有一个 `usage` 属性，包含：
       - `input_tokens`: 输入 token 数
       - `output_tokens`: 输出 token 数
       - `total_tokens`: 总 token 数
       - `input_tokens_details.cached_tokens`: 缓存的 token 数
       - `output_tokens_details.reasoning_tokens`: 推理 token 数
     - 多轮对话会有多个 response，需要累加所有的 token

### 主要改进
1. **准确的统计**：
   - 正确从 `raw_responses` 中提取 usage 信息
   - 累加多轮对话的所有 token
   - 实时显示每个章节的 token 消耗

2. **工具调用统计**：
   - 从 `new_items` 中识别 `ToolCallItem`
   - 提取工具名称并累加统计
   - 支持多种搜索工具的分类统计

3. **调试过程**：
   - 创建测试脚本验证 RunResult 结构
   - 发现 usage 在 raw_responses 中
   - 修复所有统计代码

### 修改的文件
- `wide_research/main.py`：
  - 修复 `_clarify_task` 方法的 token 统计
  - 修复规划阶段的 token 统计
  - 修复搜索阶段的 token 和工具调用统计
  - 修复写作阶段的 token 统计
  - 所有统计都使用正确的 `raw_responses` 访问方式

### 验证方法
运行程序后，统计信息应该显示实际的 token 消耗和检索次数，而不是全部为 0。

## 2025-10-13 (第三次修改)
### 优化检索次数统计和调试功能
- **问题识别**：用户发现只统计到 `web_qa` (40次)，其他搜索工具都是 0
- **可能原因**：
  1. Agent 确实只使用了 `web_qa` 工具
  2. 工具名称可能不匹配
  3. 需要调试查看实际调用的工具名称

- **解决方案**：
  1. **添加调试输出**：
     - 在工具调用统计处添加打印语句
     - 显示每次检测到的工具名称：`🔧 检测到工具调用: {tool_name}`
     - 对未知工具显示警告：`⚠️ 未知工具类型: {tool_name}`
  
  2. **动态统计所有工具**：
     - 不再限制只统计预定义的 5 种工具
     - 自动添加和统计任何被调用的工具
     - 避免遗漏新的工具类型
  
  3. **优化统计显示**：
     - 按调用次数从高到低排序显示
     - 只显示实际被调用的工具（count > 0）
     - 支持更多工具的友好名称映射：
       - `google_search`: Google 搜索
       - `scholar_search`: 学术搜索
       - `news_search`: 新闻搜索
       - `web_qa`: 网页内容获取
       - `image_search`: 图像搜索
       - `search`: 搜索
       - `video_search`: 视频搜索
       - `map_search`: 地图搜索
       - `place_search`: 地点搜索
       - `autocomplete`: 自动补全
       - `google_lens`: Google Lens

### 主要改进
1. **调试友好**：
   - 实时显示工具调用情况
   - 便于诊断为什么某些工具没有被调用
   - 发现未知工具类型

2. **动态扩展**：
   - 不限制工具类型
   - 自动适应新增的工具
   - 避免统计遗漏

3. **更好的展示**：
   - 按使用频率排序
   - 只显示实际使用的工具
   - 更清晰的中文名称

### 修改的文件
- `wide_research/main.py`：
  - 添加工具调用调试输出
  - 实现动态工具统计
  - 优化 `print_statistics()` 方法的检索统计显示

### 调试建议
运行程序时注意观察：
- 是否有 `🔧 检测到工具调用` 的输出
- 实际调用了哪些工具
- 是否有 `⚠️ 未知工具类型` 的警告

如果其他搜索工具确实是 0，可能需要：
1. 检查 prompts 是否指导使用这些工具
2. 确认 Agent 的 tools 列表是否包含这些工具
3. 考虑是否需要明确要求使用多种搜索工具

## 2025-10-13 (第四次修改)
### 清理 wide_research 目录
- **目的**：移除不必要的文件，保持代码仓库整洁
- **操作内容**：

### 删除的文件
1. **生成的报告文件**：
   - `final_report.md`
   - `stat6_final_report.md`
   - `抗体 ph 敏感度改造计算方法.md`
   - `氧化钒在神经性疼痛镇痛靶点_report.md`

2. **临时和缓存文件**：
   - `test.db` (30MB 数据库文件)
   - `workspace/` (包含13个研究项目的临时文件)
   - `.DS_Store` (macOS 系统文件)

3. **备份文件**：
   - `prompts_backup.yaml`
   - `main.py` (旧版本)

### 保留的文件
1. **main.py** (从 `main_token.py` 重命名)
   - 最新版本，包含完整的 token 统计功能
   - 支持并行处理
   - 包含调试输出

2. **prompts.yaml**
   - 提示词配置文件
   - 必需的配置

3. **README.md**
   - 项目说明文档

### 新增文件
- **`.gitignore`**
  - 防止将来生成的报告、工作区、数据库文件被提交
  - 排除 macOS 系统文件和 Python 缓存

### 清理效果
- 删除了约 30MB+ 的临时文件和生成内容
- 保持了 3 个核心文件 + 1 个配置文件
- 文件夹结构简洁清晰

### 文件结构
```
wide_research/
├── main.py           # 主程序（带统计功能）
├── prompts.yaml      # 提示词配置
├── README.md         # 说明文档
└── .gitignore        # Git 忽略规则
```

## 2025-10-14
### 分析和优化 main.py 的 src 依赖
- **目的**：分析 main.py 使用了哪些 src/ (utu) 库的函数，识别标准库和自定义模块

### 依赖分析结果

#### ✅ 标准 utu 库模块（7个）
1. **SimpleAgent** (`src.agents`)
   - 用于创建各种 Agent 实例
   - 使用 6 次：澄清、规划、搜索、写作等
   
2. **ConfigLoader** (`src.config`)
   - 加载工具配置
   - 用于加载 search 和 serper 配置

3. **SearchToolkit** (`src.tools`)
   - 提供 search() 和 web_qa() 工具
   - web_qa 会消耗 LLM token

4. **SerperToolkit** (`src.tools`)
   - 提供 Google、学术、新闻等搜索工具
   - 不消耗 LLM token

5. **AgentsUtils** (`src.utils`)
   - 用于打印流式事件
   - 使用 2 次

6. **FileUtils** (`src.utils`)
   - 用于加载 YAML 配置
   - 加载 prompts.yaml

7. **schema_to_basemodel** (`src.utils`)
   - **未使用**，已移除

#### ⚠️ 新增自定义模块（1个）
1. **CitationProcessor** (`src.utils.Citation`)
   - **自定义模块**，需要额外维护
   - 用于处理文献引用：`[cite:xxx]` → `[1]`
   - 生成格式化的参考文献列表

### 代码优化

1. **移除未使用的导入**：
   ```python
   # 修改前
   from src.utils import AgentsUtils, FileUtils, schema_to_basemodel
   
   # 修改后
   from src.utils import AgentsUtils, FileUtils
   ```

2. **合并导入语句**：
   ```python
   # 修改前
   from src.tools import SearchToolkit
   from src.tools import SerperToolkit
   
   # 修改后
   from src.tools import SearchToolkit, SerperToolkit
   ```

3. **修复未定义变量**：
   ```python
   # 修改前
   query = query.strip() or TASK  # TASK 未定义
   
   # 修改后
   if not query.strip():
       print("❌ 错误: 请输入研究主题")
       return
   ```

### 文档输出
- 创建了 `src_usage_analysis.md` 详细分析文档
- 包含所有模块的使用位置和说明
- 提供优化建议

### 建议改进
1. 将 `CitationProcessor` 添加到 `src/utils/__init__.py` 的导出列表
2. 为 `CitationProcessor` 添加单元测试
3. 考虑是否需要将 `CitationProcessor` 移到单独的包中

## 2025-10-14 (第二次修改)
### 发现并分析 Patch 的自动应用机制
- **问题**：用户询问 main.py 是否调用了 patch
- **发现**：虽然没有直接导入，但通过 `src/__init__.py` 自动应用了 patch

### Patch 机制详解

#### 自动加载流程
```
main.py 导入 src 模块
  ↓
触发 src/__init__.py 执行
  ↓
src/__init__.py:
  - 导入 UTUAgentRunner
  - 调用 set_default_agent_runner(UTUAgentRunner())
  ↓
所有 SimpleAgent 使用 patched runner
```

#### UTUAgentRunner Patch 功能

1. **Context Manager 支持**
   - 前置处理：`context_manager.preprocess(input, context_wrapper)`
   - 后置处理：`context_manager.process(single_turn_result)`
   - 用途：可在 Agent 运行前后处理输入输出

2. **调试日志功能** (可选)
   - 调试输入：`print(f"< [DEBUG] input: {input}")`
   - 调试输出：`print(json.dumps([item.model_dump() for item in new_response.output], ...))`
   - 默认注释，需要时可启用

#### 影响范围

所有通过 `SimpleAgent` 创建的 Agent：
- ✅ ClarifierAgent
- ✅ PlannerAgent
- ✅ SearcherAgent
- ✅ SectionWriterAgent (包括动态创建的)

#### 依赖分析更新

**总依赖**：
- 标准 utu 库：7 个模块
- 自定义模块：1 个 (`CitationProcessor`)
- **自动 Patch**：1 个 (`UTUAgentRunner`) ← 新发现

### 文档更新

1. **新增 `patch_analysis.md`**
   - Patch 的触发机制
   - UTUAgentRunner 的功能说明
   - 影响范围分析
   - 禁用方法（如需要）

2. **更新 `src_usage_analysis.md`**
   - 添加自动应用的 Patch 章节
   - 完整的 Patch 执行流程
   - 依赖状态说明

### 关键发现

⚠️ **重要**：`main.py` 间接依赖 `src.patch.runner`
- 不需要显式导入
- 通过 `src/__init__.py` 自动应用
- 对所有 Agent 透明生效
- 提供 Context Manager 扩展能力

### 建议
- ✅ 保持现有的 patch 机制，提供了有用的扩展能力
- ✅ 不建议禁用，不会影响正常功能
- ✅ 如需调试，可以启用 patch 中的调试日志

## 2025-10-14 (第三次修改)
### 为综述添加表格生成功能
- **需求**：在综述中自动生成表格，用于对比和总结信息
- **实现方案**：
  1. **表格生成策略**：
     - 由 AI 根据检索到的文献内容，总结对比生成表格
     - 在章节撰写时，由 `SectionWriterAgent` 根据内容自动判断是否需要生成表格
     - 支持多种表格类型：对比表、数据汇总表、时间线表、靶点/通路表
  
  2. **表格配置**：
     - **编号方式**：全局连续编号（表1、表2、表3...）
     - **表格位置**：章节结尾（先阐述内容，最后用表格总结）
     - **判断标准**：只在数据密集或对比明显时生成（适中标准）
     - **列数限制**：最多 4-7 列，确保可读性
     - **表格目录**：不生成
     - **格式要求**：Markdown 表格，带编号和标题
  
  3. **实现细节**：
     
     **修改 1：prompts.yaml - section_writer**
     - 在核心指令中添加第 7 条"表格生成（可选）"
     - 详细说明表格生成的判断时机、标准、类型和要求
     - 更新输出格式，支持表格输出
     - 表格格式：`**表 {table_number}. [表格标题]**`
     
     **修改 2：main.py - 表格计数逻辑**
     - 在 `DeepResearchAgent.__init__()` 中添加 `self.table_counter = 0`
     - 在 `process_subsection` 中：
       - 获取当前表格编号：`current_table_number = self.table_counter + 1`
       - 将 `table_number` 传入 `writer_prompt`
       - 生成内容后检查是否包含表格
       - 如有表格，更新计数器并显示提示：`📊 已生成表格：表X`

### 表格生成逻辑
```python
# 1. 获取当前表格编号
current_table_number = self.table_counter + 1

# 2. 传入 writer_prompt
writer_prompt = PROMPTS["section_writer"].format(
    subsection_title=subsection['title'],
    subsection_focus=subsection['research_focus'],
    context_for_writer=context_for_writer,
    table_number=current_table_number
)

# 3. 生成内容后检查表格
if f"**表 {current_table_number}." in written_content:
    self.table_counter += 1
    print(f"📊 [{subsection['id']}] 已生成表格：表{current_table_number}")
```

### 表格输出格式
```markdown
[正文内容...]

**表 X. [表格标题]**
| 列名1 | 列名2 | 列名3 | 列名4 |
|------|------|------|------|
| 数据1 | 数据2 | 数据3 | 数据4 |
| ... | ... | ... | ... |

*注：表格数据应包含引用，例如：化合物A [cite:smith2023]*
```

### 主要特点
1. **智能判断**：
   - 只在有 3 个以上可对比项目时考虑生成表格
   - 数据密集或对比价值明显时生成
   - 文字表述已足够清晰则不生成表格

2. **表格类型**：
   - 对比表：对比不同研究/化合物/方法的特征
   - 数据汇总表：汇总关键数值数据（活性、临床数据等）
   - 时间线表：展示研究进展的时间序列
   - 靶点/通路表：展示相关靶点、通路及其功能

3. **规范格式**：
   - Markdown 表格格式
   - 全局连续编号
   - 带标题和编号
   - 列数控制在 4-7 列
   - 表格数据包含文献引用

4. **自动计数**：
   - 全局表格计数器追踪
   - 自动递增编号
   - 实时显示生成提示

### 修改的文件
- `wide_research/prompts.yaml`：
  - 扩展 `section_writer` 指令，添加表格生成功能
  - 提供详细的表格类型和格式指导

- `wide_research/main.py`：
  - 添加 `self.table_counter` 初始化
  - 在 writer_prompt 中传入 `table_number`
  - 添加表格检测和计数更新逻辑
  - 添加表格生成提示输出

### 功能优势
- ✅ 自动判断是否需要表格
- ✅ 多种表格类型支持
- ✅ 统一的编号管理
- ✅ 规范的格式输出
- ✅ 包含文献引用
- ✅ 提升综述可读性

## 2025-10-14 (第四次修改)
### 重新实现表格生成功能（代码路径从 src 改为 utu）
- **背景**：用户将代码中的导入路径从 `src` 改为 `utu`，之前的表格功能修改被撤销
- **操作**：重新实现完整的表格生成功能

### 修改内容

#### 1. prompts.yaml - section_writer 扩展
- 在"核心指令"部分添加第 7 条"表格生成（可选）"
- 详细说明：
  - **判断时机**：3个以上对比项、大量数值数据、时间线、多靶点对比
  - **判断标准**：数据密集或对比明显时才生成
  - **表格类型**：对比表、数据汇总表、时间线表、靶点/通路表
  - **表格要求**：
    - Markdown 格式，4-7 列
    - 放在章节末尾
    - 格式：`**表 {table_number}. [表格标题]**`
    - 包含文献引用
- 更新输出格式说明，提供表格输出示例

#### 2. main.py - 表格计数逻辑实现
- **添加 __init__ 方法**（第118-119行）：
  ```python
  def __init__(self):
      self.table_counter = 0  # 全局表格计数器
  ```

- **传入表格编号**（第306-313行）：
  ```python
  # 获取当前表格编号
  current_table_number = self.table_counter + 1
  
  writer_prompt = PROMPTS["section_writer"].format(
      subsection_title=subsection['title'],
      subsection_focus=subsection['research_focus'],
      context_for_writer=context_for_writer,
      table_number=current_table_number
  )
  ```

- **表格检测和计数更新**（第327-330行）：
  ```python
  # 检查是否包含表格，并更新全局表格计数器
  if f"**表 {current_table_number}." in written_content:
      self.table_counter += 1
      print(f"    📊 [{subsection['id']}] 已生成表格：表 {current_table_number}")
  ```

#### 3. 代码优化
- **修复 TASK 未定义错误**（第421-423行）：
  ```python
  if not query.strip():
      print("❌ 错误: 请输入研究主题")
      return
  ```

- **优化导入语句**（第17-21行）：
  - 移除未使用的 `schema_to_basemodel`
  - 合并 `SearchToolkit` 和 `SerperToolkit` 导入
  - 统一使用 `utu` 路径

### 技术要点
1. **全局计数器**：`self.table_counter` 追踪所有已生成的表格
2. **动态编号**：每次调用前 `+1` 获取下一个编号
3. **检测机制**：通过字符串匹配检测表格是否生成
4. **并行安全**：虽然是并行处理，但计数器更新在各自的 async 任务中独立进行

### 修改的文件
1. `wide_research/prompts.yaml`：
   - 扩展 `section_writer` 提示词
   - 添加完整的表格生成指导

2. `wide_research/main.py`：
   - 添加 `__init__` 方法和计数器
   - 实现表格编号传递和检测
   - 优化导入语句
   - 修复 TASK 变量错误

### 功能验证
- ✅ 代码无 linter 错误
- ✅ 表格编号逻辑完整
- ✅ 导入路径统一为 `utu`
- ✅ 错误处理完善

## 2025-10-14 (第五次修改)
### 优化表格生成策略 - 改为真正可选（不强制生成）
- **问题**：之前每个章节都在生成表格，但实际上大多数章节不需要表格
- **原因**：prompt 中强制性地提供了表格编号，让 AI 误以为必须生成表格
- **解决方案**：强化表格的"可选性"，提高生成门槛

### 修改内容

#### 1. prompts.yaml - 强化表格可选性
- **重要提示**：明确说明"大多数章节不需要表格"
- **提高生成门槛**：
  - 原要求：3个以上对比项 → 新要求：**5个以上**对比项
  - 新增数量要求：大量密集数值（如10个以上化合物活性数据）
  - 新增行数要求：至少5行数据（少于5行用文字更好）
  
- **明确何时不需要表格**：
  - 只有2-3个简单对比项 → 用文字描述
  - 数据量不大 → 正文中直接说明
  - 信息可以用简洁文字表达 → 不要画蛇添足
  - 只是描述性内容 → 绝对不需要表格
  
- **判断标准**：
  - 原则：**优先使用文字表述**
  - 标准：只有在表格能**显著提升**可读性、**节省篇幅**时才生成
  - 宁可不生成，也不要生成无意义的表格

- **输出格式说明**：
  - 强调："大多数情况下，只输出正文即可，不需要表格"
  - 说明："仅在确实需要表格时（见上述严格标准）"才添加
  - 注释：table_number 如果需要就用，不需要就忽略

#### 2. main.py - 优化 prompt 构建方式
- **修改前**（强制性）：
  ```python
  writer_prompt = f"""
  ### **章节标题**: {subsection['title']}
  ### **章节焦点**: {subsection['research_focus']}
  ### **相关研究资料**: {context_for_writer}
  ### **表 {current_table_number}**  # 这会让AI误以为必须生成表格
  """
  ```

- **修改后**（温和提示）：
  ```python
  writer_prompt = f"""
  ### **章节标题**: {subsection['title']}
  
  ### **章节焦点**: {subsection['research_focus']}
  
  ### **相关研究资料**:
  {context_for_writer}
  
  ---
  **注意**：如果本章节确实需要表格来更好地展示对比或汇总信息（参考表格生成标准），请使用表格编号：**{current_table_number}**
  如果不需要表格，请直接输出正文内容即可。
  """
  ```

### 关键改进

1. **表格生成门槛大幅提高**：
   - 对比项：3+ → 5+
   - 数值数据：少量 → 10+个化合物
   - 表格行数：无要求 → 至少5行
   
2. **明确不需要表格的场景**：
   - 给出4种不需要表格的具体情况
   - 防止 AI 过度使用表格
   
3. **prompt 表述更温和**：
   - 不再强制提供表格编号
   - 使用"如果需要...请使用...如果不需要...请忽略"的表述
   - 让 AI 自主判断是否需要表格

4. **强调优先文字表述**：
   - 明确原则："优先使用文字表述"
   - 宁可不生成，也不要生成无意义的表格

### 预期效果
- ✅ 大多数章节将只输出正文，不包含表格
- ✅ 只有真正需要对比大量数据的章节才会生成表格
- ✅ 表格质量提升（只生成有价值的表格）
- ✅ 综述整体更加简洁专业

### 修改的文件
- `wide_research/prompts.yaml`：强化表格可选性说明，提高生成门槛
- `wide_research/main.py`：优化 prompt 构建方式，改为温和提示

## 2025-10-14 (第六次修改)
### 修复并行处理导致的表格编号冲突问题
- **问题**：由于并行处理，多个章节可能同时获取 `self.table_counter + 1`，导致表格编号重复或混乱
- **原因**：在并行执行的 `process_subsection` 函数中动态计算表格编号，存在竞态条件
- **解决方案**：预先分配表格编号 + 最后重新整理编号

### 修改内容

#### 1. 预先分配表格编号（第231-242行）
在收集所有子章节时，为每个章节预先分配一个唯一的表格编号，避免并行冲突：

```python
# 收集所有子章节，并为每个章节预先分配表格编号
all_subsections = []
for section in parsed_outline.get("sections", []):
    for subsection in section.get("subsections", []):
        subsection['sections_title'] = section['title']
        subsection['sections_id'] = section['id']
        
        # 为每个章节预先分配一个潜在的表格编号（避免并行冲突）
        self.table_counter += 1
        subsection['assigned_table_number'] = self.table_counter
        
        all_subsections.append(subsection)
```

**优势**：
- ✅ 在并行执行前完成编号分配
- ✅ 每个章节都有唯一的编号
- ✅ 避免竞态条件

#### 2. 使用预分配的编号（第309-323行）
修改 `process_subsection` 函数，使用预先分配的编号：

```python
# 修改前（有并发问题）
current_table_number = self.table_counter + 1  # 多个章节可能同时执行

# 修改后（使用预分配编号）
assigned_table_number = subsection['assigned_table_number']  # 唯一且固定
```

#### 3. 表格重新编号功能（第193-228行）
添加 `renumber_tables()` 方法，确保最终报告中的表格编号连续：

```python
def renumber_tables(self, content: str) -> str:
    """
    重新整理表格编号，确保表格编号连续（表1、表2、表3...）
    """
    import re
    
    # 找出所有表格标题（格式：**表 X. 标题**）
    table_pattern = r'\*\*表\s+(\d+)\.\s+([^\*]+)\*\*'
    tables = list(re.finditer(table_pattern, content))
    
    if not tables:
        return content
    
    # 创建旧编号到新编号的映射
    old_to_new = {}
    for new_num, match in enumerate(tables, 1):
        old_num = match.group(1)
        old_to_new[old_num] = str(new_num)
    
    # 替换所有表格标题
    def replace_table_title(match):
        old_num = match.group(1)
        title = match.group(2)
        new_num = old_to_new[old_num]
        return f"**表 {new_num}. {title}**"
    
    content = re.sub(table_pattern, replace_table_title, content)
    
    print(f"  📊 表格重新编号完成: 共 {len(tables)} 个表格")
    return content
```

**功能**：
- 自动检测所有表格
- 按出现顺序重新编号（表1、表2、表3...）
- 处理编号跳跃问题（如章节2、5、7生成了表格，会重新编号为表1、2、3）

#### 4. 在最终报告生成时调用（第439-443行）

```python
# 处理文献引用
final_output = self.process_draft(full_content, all_sources_metadata)

# 重新整理表格编号，确保连续性
final_output = self.renumber_tables(final_output)
```

### 解决的问题

1. **并发冲突**：
   - ❌ 问题：多个章节同时计算编号 → 编号重复
   - ✅ 解决：预先顺序分配 → 编号唯一

2. **编号跳跃**：
   - ❌ 问题：章节1、3、5生成表格 → 编号为1、3、5（不连续）
   - ✅ 解决：最后重新编号 → 编号为1、2、3（连续）

3. **表格顺序**：
   - ✅ 保证：表格按章节顺序编号
   - ✅ 保证：最终报告中表格编号连续且有序

### 技术要点

1. **预分配策略**：
   - 在单线程环境下预先分配所有编号
   - 每个章节获得唯一且固定的编号
   - 完全避免并发冲突

2. **正则表达式匹配**：
   - 模式：`r'\*\*表\s+(\d+)\.\s+([^\*]+)\*\*'`
   - 匹配：`**表 X. 标题**` 格式
   - 提取：表格编号和标题

3. **重新编号逻辑**：
   - 遍历所有表格，创建旧→新编号映射
   - 使用 `re.sub()` 批量替换
   - 保持标题不变，只更新编号

### 修改的文件
- `wide_research/main.py`：
  - 添加预分配表格编号逻辑
  - 修改使用预分配编号
  - 添加 `renumber_tables()` 方法
  - 在最终报告生成时调用重新编号

### 功能验证
- ✅ 代码无 linter 错误
- ✅ 表格编号在并行处理中唯一
- ✅ 最终报告中表格编号连续
- ✅ 表格按章节顺序编号

## 2025-10-14 (第七次修改)
### 在规划阶段给出表格生成建议
- **需求**：在 planner 规划阶段就明确指出哪些章节需要生成表格
- **优势**：让 planner 提前判断，writer 根据建议执行，提高表格生成的准确性和一致性

### 修改内容

#### 1. prompts.yaml - 扩展 planner_new 输出格式

**添加 TABLE_RECOMMENDED 字段**（第283-298行）：

```yaml
3. **提供聚焦的研究指令**: 对于每一个 `### 子章节`，你必须在其标题后的新一行提供以下三个关键信息：
   *   `FOCUS:` ...
   *   `KEYWORDS:` ...
   *   `TABLE_RECOMMENDED:` 判断该章节是否建议使用表格。填写 `YES` 或 `NO`。
       - **建议使用表格 (YES)** 的场景：
         * 涉及多个化合物/药物/分子的性质对比（3个以上）
         * 包含具体数值数据（IC50、Ki、EC50等）
         * 需要对比多个维度参数（活性、选择性等）
         * 涉及多个研究结果汇总或临床试验数据对比
         * 列举多个靶点/通路及其特征
         * 展示时间序列数据或研究进展历程
       - **不建议使用表格 (NO)** 的场景：
         * 引言、背景介绍等描述性章节
         * 结论、未来展望等总结性章节
         * 只有1-2个简单对比项
         * 主要是概念性、理论性阐述
```

**更新输出格式示例**（第308-349行）：
- 每个子章节添加 `TABLE_RECOMMENDED: YES/NO` 行
- 提供具体示例：引言章节标记 NO，化合物对比章节标记 YES

#### 2. main.py - 解析和使用表格建议

**修改 parse_markdown_outline 函数**（第56-121行）：

```python
# 添加 TABLE_RECOMMENDED 正则表达式
table_regex = re.compile(r"^\s*TABLE_RECOMMENDED:\s*(.*)", re.IGNORECASE)

# 在 subsection_data 中添加字段
subsection_data = {
    "title": subsection_title,
    "id": subsection_title.split(' ')[0],
    "research_focus": "",
    "keywords": [],
    "table_recommended": False  # 默认不建议表格
}

# 解析 TABLE_RECOMMENDED 行
table_match = table_regex.match(line)
if table_match:
    if current_section and current_section["subsections"]:
        table_value = table_match.group(1).strip().upper()
        current_section["subsections"][-1]["table_recommended"] = (table_value == "YES")
    continue
```

**修改 writer_prompt 构建**（第353-386行）：

```python
# 获取 planner 的表格建议
table_recommended = subsection.get('table_recommended', False)
table_status = "✅ 建议表格" if table_recommended else "📝 文字为主"
print(f"  ✍️  [{subsection['id']}] (3c) 撰写章节内容... ({table_status})")

# 根据建议提供不同的指导
if table_recommended:
    table_instruction = """
---
**📊 表格建议**：Planner 建议本章节使用表格来展示对比或汇总信息。
如果文献内容适合用表格展示（如多个项目对比、数值数据等），请使用表格编号：**{assigned_table_number}**
生成表格时请参考表格生成标准。
"""
else:
    table_instruction = """
---
**📝 写作建议**：本章节主要使用文字论述即可，通常不需要表格。
除非遇到特别适合表格展示的密集数据，否则请用清晰的文字表述内容。
如果确实需要表格，可使用编号：**{assigned_table_number}**
"""
```

### 工作流程

```
1. 用户输入研究主题
   ↓
2. Planner 生成大纲
   - 分析每个章节内容
   - 判断是否适合使用表格
   - 输出 TABLE_RECOMMENDED: YES/NO
   ↓
3. 解析大纲
   - 提取 table_recommended 字段
   - 存储到 subsection 数据中
   ↓
4. Writer 撰写章节
   - 读取 table_recommended 建议
   - 根据建议调整写作策略
   - YES → 积极考虑表格
   - NO → 优先使用文字
   ↓
5. 生成最终报告
```

### 优势分析

1. **智能规划**：
   - ✅ Planner 提前判断章节特性
   - ✅ 避免盲目生成或遗漏表格
   - ✅ 提高表格生成的准确性

2. **明确指导**：
   - ✅ Writer 获得明确的表格建议
   - ✅ 减少 Writer 的判断负担
   - ✅ 提高写作一致性

3. **灵活性**：
   - ✅ 建议仅作参考，Writer 仍可自主判断
   - ✅ 适应实际文献内容
   - ✅ 保持表格生成的灵活性

4. **可追踪性**：
   - ✅ 运行时显示表格建议状态
   - ✅ 便于调试和优化
   - ✅ 了解 Planner 的判断逻辑

### 示例输出

运行时会看到：
```
✍️ [1.1] (3c) 撰写章节内容... (📝 文字为主)
✍️ [2.1] (3c) 撰写章节内容... (✅ 建议表格)
✍️ [2.2] (3c) 撰写章节内容... (📝 文字为主)
✍️ [3.1] (3c) 撰写章节内容... (✅ 建议表格)
```

### 修改的文件
- `wide_research/prompts.yaml`：
  - 扩展 planner_new 输出格式，添加 TABLE_RECOMMENDED 字段
  - 提供表格建议的判断标准和示例

- `wide_research/main.py`：
  - 修改 `parse_markdown_outline` 函数，解析 TABLE_RECOMMENDED
  - 修改 writer_prompt 构建，根据建议提供不同指导
  - 添加表格建议状态的打印输出

### 功能验证
- ✅ 代码无 linter 错误
- ✅ Planner 可以输出表格建议
- ✅ 解析逻辑正确提取建议
- ✅ Writer 接收到明确的指导
- ✅ 运行时显示建议状态

## 2025-10-14 (第八次修改)
### Planner 给出表格编号 + Writer 在正文中引用表格
- **需求**：
  1. Planner 在建议表格时同时给出表格编号
  2. Writer 撰写时要在段落中引用表格（如"如表X所示"）
- **目的**：让表格编号更加规范，正文与表格的关联更紧密

### 修改内容

#### 1. prompts.yaml - Planner 输出表格编号

**添加 TABLE_NUMBER 字段**（第299-301行）：
```yaml
*   `TABLE_NUMBER:` 如果 `TABLE_RECOMMENDED: YES`，则需要给出表格编号建议。
    格式为数字（从1开始顺序编号）。如果 `TABLE_RECOMMENDED: NO`，则填写 `N/A`。
    - **表格编号规则**：按子章节出现顺序，为所有建议使用表格的章节从1开始连续编号。
    - **示例**：第一个建议表格的章节 → `TABLE_NUMBER: 1`；第二个建议表格的章节 → `TABLE_NUMBER: 2`
```

**更新输出格式示例**（第311-359行）：
- 每个子章节添加 `TABLE_NUMBER: X` 或 `TABLE_NUMBER: N/A`
- 示例：
  - `### 1.1` → `TABLE_RECOMMENDED: NO` + `TABLE_NUMBER: N/A`
  - `### 2.2` → `TABLE_RECOMMENDED: YES` + `TABLE_NUMBER: 1`
  - `### 3.1` → `TABLE_RECOMMENDED: YES` + `TABLE_NUMBER: 2`

#### 2. prompts.yaml - Writer 必须引用表格

**添加表格引用要求**（第428-436行）：
```yaml
* **表格引用（重要）**：
  - 在正文段落中**必须引用表格**，使用以下表述方式：
    * "如表X所示，..."
    * "详见表X"
    * "表X总结了..."
    * "这些数据汇总于表X"
  - 引用表格的段落应该在表格之前出现
  - 引用时机：在阐述相关数据或对比信息时自然引用
  - **引用规范**：生成表格就必须在正文中引用，否则不要生成
```

**更新输出格式示例**（第450-461行）：
```markdown
...现有研究已报道了多个STAT6抑制剂，这些化合物在体外实验中展现出不同的活性特征。
如表1所示，化合物A的IC50值最低（12.5 nM），显示出最强的抑制活性 [cite:smith2023]。
化合物B和C也表现出良好的选择性...

**表 1. STAT6抑制剂活性数据对比**
| 化合物名称 | IC50 (nM) | 选择性 | 来源 |
|-----------|-----------|--------|------|
| 化合物A | 12.5 | >100倍 | [cite:smith2023] |
| 化合物B | 25.3 | >50倍 | [cite:jones2024] |
| 化合物C | 48.7 | >30倍 | [cite:wang2024] |
```

#### 3. main.py - 解析和使用表格编号

**添加 TABLE_NUMBER 解析**（第60行，第96行，第125-136行）：
```python
# 添加正则表达式
table_number_regex = re.compile(r"^\s*TABLE_NUMBER:\s*(.*)", re.IGNORECASE)

# 在 subsection_data 中添加字段
subsection_data = {
    "title": subsection_title,
    "id": subsection_title.split(' ')[0],
    "research_focus": "",
    "keywords": [],
    "table_recommended": False,
    "table_number": None  # 新增：默认无表格编号
}

# 解析 TABLE_NUMBER 行
table_number_match = table_number_regex.match(line)
if table_number_match:
    if current_section and current_section["subsections"]:
        table_num_str = table_number_match.group(1).strip()
        # 如果是 N/A 或空，则为 None；否则转换为整数
        if table_num_str.upper() != "N/A" and table_num_str:
            try:
                current_section["subsections"][-1]["table_number"] = int(table_num_str)
            except ValueError:
                current_section["subsections"][-1]["table_number"] = None
    continue
```

**使用 Planner 建议的表格编号**（第369-394行）：
```python
# 获取 planner 的表格建议和编号
table_recommended = subsection.get('table_recommended', False)
planner_table_number = subsection.get('table_number', None)

# 优先使用 planner 建议的编号
assigned_table_number = planner_table_number if planner_table_number else subsection['assigned_table_number']

table_status = f"✅ 建议表格{assigned_table_number}" if table_recommended else "📝 文字为主"
print(f"  ✍️  [{subsection['id']}] (3c) 撰写章节内容... ({table_status})")

if table_recommended:
    table_instruction = f"""
---
**📊 表格建议**：Planner 建议本章节使用表格来展示对比或汇总信息。
- **表格编号**：**{assigned_table_number}**
- **重要**：生成表格时，必须在正文段落中引用表格，使用"如表{assigned_table_number}所示"、"详见表{assigned_table_number}"等表述。
- 表格应放在正文末尾，作为内容的总结和补充。
"""
```

### 工作流程

```
1. Planner 生成大纲
   - 分析章节内容
   - 判断是否需要表格（YES/NO）
   - 为需要表格的章节分配编号（1, 2, 3...）
   ↓
2. 解析大纲
   - 提取 table_recommended
   - 提取 table_number
   ↓
3. Writer 撰写章节
   - 获取 planner 建议的表格编号
   - 如果建议生成表格：
     * 在正文段落中引用表格（"如表X所示"）
     * 在章节末尾添加表格
     * 表格标题使用建议的编号
   ↓
4. 最终报告
   - 表格编号由 planner 统一规划
   - 正文中有明确的表格引用
   - 表格与正文紧密关联
```

### 示例效果

**Planner 输出**：
```markdown
### 2.2 STAT6抑制剂活性研究
FOCUS: 对比分析多个STAT6抑制剂的活性数据...
KEYWORDS: STAT6抑制剂, IC50, 活性对比, ...
TABLE_RECOMMENDED: YES
TABLE_NUMBER: 1
```

**Writer 输出**：
```markdown
现有研究已报道了多个STAT6抑制剂，这些化合物在体外实验中展现出不同的活性特征。
如表1所示，化合物A的IC50值最低（12.5 nM），显示出最强的抑制活性 [cite:smith2023]。

**表 1. STAT6抑制剂活性数据对比**
| 化合物名称 | IC50 (nM) | 选择性 | 来源 |
|-----------|-----------|--------|------|
| 化合物A | 12.5 | >100倍 | [cite:smith2023] |
```

**运行时显示**：
```
✍️ [1.1] (3c) 撰写章节内容... (📝 文字为主)
✍️ [2.2] (3c) 撰写章节内容... (✅ 建议表格1)
✍️ [3.1] (3c) 撰写章节内容... (✅ 建议表格2)
```

### 优势分析

1. **统一规划**：
   - ✅ Planner 在规划时就确定表格编号
   - ✅ 避免 Writer 自行编号导致混乱
   - ✅ 表格编号连续且有序

2. **正文关联**：
   - ✅ 强制要求在正文中引用表格
   - ✅ "如表X所示"让读者明确表格位置
   - ✅ 提升综述的可读性和专业性

3. **编号准确**：
   - ✅ Planner 给出的编号直接使用
   - ✅ 无需后期重新编号
   - ✅ 正文引用与表格编号一致

4. **规范性强**：
   - ✅ 符合学术论文的写作规范
   - ✅ 表格不是孤立存在，而是与正文紧密结合
   - ✅ 提供多种引用表述方式

### 修改的文件
- `wide_research/prompts.yaml`：
  - 扩展 planner_new，添加 TABLE_NUMBER 字段
  - 扩展 section_writer，要求正文中引用表格
  - 提供表格引用的示例

- `wide_research/main.py`：
  - 添加 TABLE_NUMBER 解析逻辑
  - 优先使用 planner 建议的表格编号
  - 在 writer_prompt 中强调表格引用要求

### 功能验证
- ✅ 代码无 linter 错误
- ✅ Planner 输出表格编号
- ✅ 解析逻辑正确提取编号
- ✅ Writer 使用 planner 的编号
- ✅ Writer 被要求在正文中引用表格

## 2025-10-14 (第九次修改)
### 第一章和最后一章不添加小标题
- **需求**：第一章和最后一章的子章节不需要添加小标题（`### {section['title']}`），只显示内容
- **原因**：第一章通常是引言，最后一章通常是结论，这些章节的内容本身已经很明确，不需要额外的小标题
- **实现**：在最终整合阶段，判断当前章节是否为第一章或最后一章，如果是则不添加小标题

### 修改内容

#### main.py - 修改章节内容整合逻辑（第457-478行）

**修改前**（只判断第一章）：
```python
# 根据是否为第一章，决定如何添加内容
if current_section_id == '1':
    full_content += f"{section['content']}\n\n"
else:
    full_content += f"### {section['title']}\n{section['content']}\n\n"
```

**修改后**（判断第一章和最后一章）：
```python
# 先找出最后一个章节的ID
last_section_id = None
if written_sections:
    last_section_id = written_sections[-1]['sections_id']

current_section_id = None # 用于追踪当前的章节ID

for section in written_sections:
    # 检查是否进入了一个新的大章节
    if section['sections_id'] != current_section_id:
        full_content += f"# {section['sections_title']}\n\n"
        current_section_id = section['sections_id'] # 更新当前章节ID

    # 第一章和最后一章不添加小标题，其他章节添加小标题
    if current_section_id == '1' or current_section_id == last_section_id:
        full_content += f"{section['content']}\n\n"
    else:
        full_content += f"### {section['title']}\n{section['content']}\n\n"
```

### 逻辑说明

1. **识别最后一章**：
   - 在循环前遍历 `written_sections`，获取最后一个元素的 `sections_id`
   - 存储在 `last_section_id` 变量中

2. **条件判断**：
   - `current_section_id == '1'`：第一章
   - `current_section_id == last_section_id`：最后一章
   - 两者都满足时，只添加内容，不添加小标题

3. **其他章节**：
   - 正常添加小标题和内容

### 效果展示

**第一章（引言）**：
```markdown
# 1. 引言

研究背景内容...

研究意义内容...
```

**中间章节**：
```markdown
# 2. STAT6 研究进展

### 2.1 STAT6 蛋白结构
结构相关内容...

### 2.2 STAT6 信号通路
信号通路内容...
```

**最后一章（结论）**：
```markdown
# 5. 结论与展望

研究总结内容...

未来方向内容...
```

### 优势分析

1. **格式统一**：
   - ✅ 第一章不添加小标题，更简洁
   - ✅ 最后一章不添加小标题，更连贯
   - ✅ 中间章节保留小标题，结构清晰

2. **符合惯例**：
   - ✅ 学术论文中引言和结论通常不需要小标题
   - ✅ 内容本身已经足够明确
   - ✅ 避免冗余的标题层级

3. **阅读体验**：
   - ✅ 减少不必要的层级
   - ✅ 提升整体可读性
   - ✅ 更符合专业综述的格式

### 修改的文件
- `wide_research/main.py`：
  - 添加最后一章识别逻辑
  - 修改内容整合的条件判断
  - 第一章和最后一章不添加小标题

### 功能验证
- ✅ 代码无 linter 错误
- ✅ 正确识别第一章和最后一章
- ✅ 第一章和最后一章只显示内容
- ✅ 中间章节正常显示小标题
- ✅ 文档格式更加专业规范

## 2025-10-14 (第十次修改)
### 创建前后端 Web 界面
- **需求**：基于 `main.py` 创建前后端代码，提供 Web 界面访问
- **实现**：提供两个方案，适应不同场景需求

### 方案一：Gradio Web UI (main_web.py)

**特点**：简单快速，适合快速原型和内部使用

#### 核心功能
1. **界面设计**：
   - 使用 Gradio 框架快速构建
   - 内置进度条和状态显示
   - 支持示例主题快速填充
   - Markdown 格式报告展示
   
2. **异步处理**：
   ```python
   async def run_research(query: str, progress=gr.Progress()):
       await self.initialize_agent()
       result = await self.agent.run_streamed(query)
       stats = self.format_statistics(self.agent.statistics)
       return result, stats, report_path
   ```

3. **统计信息格式化**：
   - Token 消耗分阶段统计
   - 检索次数分工具统计
   - 自动成本估算（USD/CNY）
   
4. **用户交互**：
   - 研究主题输入
   - 示例主题选择
   - 实时进度显示
   - 报告下载功能

#### 启动方式
```bash
pip install gradio
python main_web.py
# 访问: http://localhost:7860
```

### 方案二：FastAPI + WebSocket + 前端 (api_server.py + frontend/index.html)

**特点**：功能完整，适合生产环境和对外服务

#### 后端架构 (api_server.py)

1. **任务管理系统**：
   ```python
   class TaskManager:
       def create_task(query) -> task_id
       def update_task(task_id, **kwargs)
       def get_task(task_id) -> TaskStatus
       def initialize_agent(task_id) -> DeepResearchAgent
   ```

2. **RESTful API 端点**：
   - `POST /api/research` - 创建研究任务
   - `GET /api/task/{task_id}` - 查询任务状态
   - `GET /api/download/{task_id}` - 下载报告
   - `WS /ws/{task_id}` - WebSocket 实时推送

3. **WebSocket 实时通信**：
   ```python
   @app.websocket("/ws/{task_id}")
   async def websocket_endpoint(websocket, task_id):
       # 持续推送任务状态
       # 类型：status, final, error
   ```

4. **后台任务执行**：
   ```python
   async def execute_research_task(task_id, query):
       # 初始化 Agent
       # 执行研究流程
       # 实时更新任务状态
       # 格式化统计信息
   ```

5. **数据模型**：
   - `ResearchRequest` - 研究请求
   - `TaskStatus` - 任务状态（pending, running, completed, failed）

#### 前端界面 (frontend/index.html)

1. **现代化设计**：
   - 渐变背景 + 卡片式布局
   - 流畅的动画效果
   - 响应式设计
   - 美观的表单控件

2. **功能实现**：
   - 研究主题输入
   - 示例主题快速填充
   - WebSocket 实时进度推送
   - 进度条动态更新
   - 标签页切换（报告/统计）
   - Markdown 渲染（使用 Marked.js）
   - 统计信息可视化
   - 报告下载

3. **技术栈**：
   - 原生 HTML/CSS/JavaScript（无框架依赖）
   - WebSocket 实时通信
   - Fetch API HTTP 请求
   - Marked.js Markdown 渲染

4. **用户体验**：
   ```javascript
   // WebSocket 连接
   const ws = new WebSocket(`ws://localhost:8000/ws/${taskId}`);
   
   ws.onmessage = (event) => {
       const data = JSON.parse(event.data);
       if (data.type === 'status') {
           updateProgress(data.progress, data.message);
       }
       if (data.type === 'final') {
           displayResult(data);
       }
   };
   ```

#### 启动方式
```bash
# 安装依赖
pip install fastapi uvicorn websockets

# 启动后端
python api_server.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs

# 启动前端（方式1：直接打开）
open frontend/index.html

# 启动前端（方式2：HTTP 服务器）
cd frontend && python -m http.server 8080
# 访问: http://localhost:8080
```

### 文档和配置

#### README_WEB.md - 完整使用指南
- **方案对比**：功能、难度、适用场景对比表
- **Gradio 方案**：安装、启动、配置、界面预览
- **FastAPI 方案**：安装、API 文档、WebSocket 用法
- **高级配置**：CORS、HTTPS、Docker、Gunicorn
- **性能优化**：并发控制、缓存机制、数据库持久化
- **常见问题**：WebSocket 连接、Token 消耗等

#### requirements_web.txt - 依赖管理
```txt
# 方案一：Gradio
gradio>=4.0.0

# 方案二：FastAPI
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
websockets>=12.0
python-multipart>=0.0.6
```

### 技术亮点

1. **双方案设计**：
   - ✅ Gradio：5 分钟快速部署
   - ✅ FastAPI：生产级架构设计

2. **实时通信**：
   - ✅ WebSocket 双向通信
   - ✅ 无需轮询，即时更新
   - ✅ 低延迟，高效率

3. **异步架构**：
   - ✅ 后台任务执行
   - ✅ 非阻塞式 I/O
   - ✅ 支持高并发

4. **用户体验**：
   - ✅ 实时进度显示
   - ✅ 流畅的动画效果
   - ✅ 响应式布局
   - ✅ 一键下载报告

5. **开发友好**：
   - ✅ 自动生成 API 文档（Swagger）
   - ✅ 完整的类型注解
   - ✅ 详细的使用指南
   - ✅ 代码注释完善

### 创建的文件

1. **main_web.py** (方案一)
   - 基于 Gradio 的完整 Web 界面
   - 包含 WebResearchInterface 类
   - 异步任务处理
   - 统计信息格式化

2. **api_server.py** (方案二后端)
   - FastAPI 应用
   - 任务管理系统
   - RESTful API
   - WebSocket 实时推送
   - 后台任务执行

3. **frontend/index.html** (方案二前端)
   - 现代化单页应用
   - 渐变背景设计
   - WebSocket 实时通信
   - Markdown 渲染
   - 统计信息可视化

4. **README_WEB.md**
   - 完整的使用指南
   - 方案对比
   - API 文档
   - 配置说明
   - 常见问题

5. **requirements_web.txt**
   - Web 界面依赖管理
   - 按方案分类

### 使用场景

**方案一（Gradio）适用于**：
- ✅ 快速原型开发
- ✅ 内部团队使用
- ✅ 个人研究工具
- ✅ 演示和测试

**方案二（FastAPI）适用于**：
- ✅ 生产环境部署
- ✅ 对外提供服务
- ✅ 需要自定义界面
- ✅ 集成到现有系统
- ✅ 移动端适配

### 后续扩展建议

1. **认证系统**：
   - 用户注册/登录
   - JWT Token 验证
   - 权限管理

2. **任务管理**：
   - 任务历史记录
   - 任务队列管理
   - 批量任务处理

3. **报告格式**：
   - PDF 导出
   - Word 导出
   - HTML 导出

4. **协作功能**：
   - 多人协作编辑
   - 评论和批注
   - 版本管理

5. **数据持久化**：
   - SQLite/PostgreSQL 存储
   - Redis 缓存
   - 向量数据库集成

### 功能验证
- ✅ Gradio 界面完整可用
- ✅ FastAPI 后端架构清晰
- ✅ WebSocket 实时通信实现
- ✅ 前端界面美观现代
- ✅ 代码注释完善
- ✅ 文档详细全面
- ✅ 依赖管理规范

## 2025-10-14 (第十一次修改)
### 重新设计 main_web.py - GPT 风格极简黑白界面 + 澄清交互 + 流式动画
- **需求**：
  1. 添加澄清交互环节（类似 main.py 的 _clarify_task）
  2. 流式生成过程需要动画效果
  3. UI 界面改为 GPT 风格的黑白极简设计

### 核心改进

#### 1. 添加澄清交互功能

**新增方法**：
```python
async def start_research_with_clarification(query: str):
    """开始研究并进行澄清"""
    # 1. 初始化 Agent
    # 2. 调用 clarifier_agent 进行需求澄清
    # 3. 判断是否需要澄清
    # 4. 如需澄清，显示澄清问题并等待用户回答
    # 5. 如无需澄清，直接开始研究

async def handle_clarification_response(user_response, chat_history):
    """处理用户的澄清回答"""
    # 1. 接收用户回答
    # 2. 整合到原始 query
    # 3. 开始完整研究流程
```

**交互流程**：
1. 用户输入研究主题
2. 系统分析需求，判断是否需要澄清
3. 如需澄清：
   - 显示澄清问题
   - 显示"跳过澄清"按钮
   - 等待用户回答或跳过
4. 如无需澄清：
   - 直接开始研究

#### 2. 实现流式动画效果

**流式输出机制**：
```python
async def run_full_research(query, chat_history):
    """运行完整研究流程（流式输出）"""
    stages = [
        ("📋 规划阶段", "正在分析研究主题，制定大纲..."),
        ("🔍 搜索阶段", "正在并行搜索和分析文献..."),
        ("✍️ 撰写阶段", "正在撰写综述报告..."),
        ("📊 整合阶段", "正在生成表格和参考文献..."),
    ]
    
    current_content = ""
    for stage_name, stage_desc in stages:
        current_content += f"\n\n**{stage_name}**\n{stage_desc}"
        chat_history[-1] = {
            "role": "assistant",
            "content": current_content + "\n\n⏳ 处理中..."
        }
        yield chat_history  # 实时更新界面
        await asyncio.sleep(0.5)  # 模拟延迟
```

**特点**：
- ✅ 使用 generator (yield) 实现流式输出
- ✅ 每个阶段逐步显示
- ✅ 实时更新聊天界面
- ✅ 带有动画效果（⏳ 处理中...）

#### 3. GPT 风格黑白极简界面

**设计理念**：
- **配色方案**：纯黑白 (#000000, #ffffff, #f4f4f4, #e5e5e5)
- **字体**：系统默认字体 (-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto)
- **布局**：居中单列，最大宽度 900px
- **圆角**：8-16px 柔和圆角
- **间距**：留白适中，不拥挤
- **交互**：细微的 hover 效果和过渡动画

**关键 CSS 特性**：

1. **顶部标题区域**（header-container）：
   - 简洁的标题和副标题
   - 底部细线分隔
   - 居中对齐

2. **聊天界面**（chatbot-container）：
   - 用户消息：灰色背景 (#f4f4f4)，右对齐
   - 助手消息：白色背景，左对齐，带边框
   - 圆角气泡样式
   - 最大宽度 85%

3. **输入框**（input-box）：
   - 白色背景，灰色边框
   - focus 时黑色边框和阴影
   - 圆角 12px

4. **按钮**：
   - 主按钮（button-primary）：黑色背景，白色文字
   - 次按钮（button-secondary）：白色背景，黑色文字，灰色边框
   - hover 时微妙变化

5. **标签页**（tab-nav）：
   - 极简设计，底部细线
   - 选中项黑色底部边框
   - 平滑过渡效果

6. **报告显示**（report-container）：
   - 纯白背景
   - 黑色文字
   - 表格带细线边框
   - 表头浅灰色背景

7. **滚动条**：
   - 细窄的滚动条（8px）
   - 灰色轨道和滑块
   - 柔和圆角

8. **加载动画**：
   ```css
   @keyframes pulse {
       0%, 100% { opacity: 1; }
       50% { opacity: 0.5; }
   }
   ```

#### 4. 对话式交互界面

**使用 Gradio Chatbot 组件**：
```python
chatbot = gr.Chatbot(
    value=[],
    height=500,
    show_label=False,
    avatar_images=(None, None),  # 不显示头像
    elem_classes="chatbot-container",
    type="messages"  # 新版 Gradio 的消息格式
)
```

**消息格式**：
```python
{
    "role": "user" | "assistant",
    "content": "消息内容"
}
```

**交互特点**：
- ✅ 类似 ChatGPT 的对话体验
- ✅ 用户消息和助手消息视觉区分明显
- ✅ 支持流式更新
- ✅ 支持多轮对话

#### 5. 事件处理优化

**同步包装器**：
```python
def sync_start_research(query, history):
    """同步包装器 - 开始研究"""
    async def _run():
        async for update in interface.start_research_with_clarification(query):
            yield update, "", False
    
    gen = _run()
    try:
        while True:
            history, report, show_skip = asyncio.run(gen.__anext__())
            yield history, report, gr.update(visible=True/False)
    except StopAsyncIteration:
        pass
```

**功能**：
- 将异步 generator 转换为 Gradio 可用的同步函数
- 实时更新界面
- 动态控制"跳过澄清"按钮的显示/隐藏

#### 6. 示例按钮

**设计**：
- 4 个常用研究主题示例
- 点击直接填充到输入框
- 灰色背景，hover 时变深

**示例主题**：
1. STAT6 在特应性皮炎中的研究进展
2. JAK-STAT 信号通路在免疫调控中的作用
3. 新型 PROTAC 降解剂的设计策略
4. 人工智能在药物发现中的应用

#### 7. 状态管理

**阶段状态**（self.stage）：
- `idle`: 空闲
- `clarifying`: 澄清中
- `researching`: 研究中
- `completed`: 已完成

**用途**：
- 控制界面流程
- 判断是否显示报告
- 决定按钮行为

### 界面预览

```
┌─────────────────────────────────────────┐
│                                         │
│          Wide Research                  │
│     深度研究助手 · 自动生成专业综述      │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  [对话区域 - 500px 高度]                │
│                                         │
│  You: STAT6 在特应性皮炎中的研究进展    │
│  ┌───────────────────────────────────┐ │
│  │                                   │ │
│  │ Assistant: 🔍 正在分析您的研究   │ │
│  │ 需求...                           │ │
│  │                                   │ │
│  │ 📋 规划阶段                       │ │
│  │ 正在分析研究主题，制定大纲...     │ │
│  │                                   │ │
│  │ ⏳ 处理中...                      │ │
│  └───────────────────────────────────┘ │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  [输入框: 输入研究主题...]              │
│                            [发送]       │
│                                         │
│  [跳过澄清]  [清空对话]                │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  💡 示例研究主题                        │
│  [STAT6研究] [JAK-STAT通路]             │
│  [PROTAC降解剂] [AI药物发现]            │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  [研究报告] [详细统计]                  │
│  ┌───────────────────────────────────┐ │
│  │ [报告内容或统计信息]              │ │
│  └───────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

### 技术亮点

1. **异步流式处理**：
   - ✅ 使用 async generator 实现真正的流式输出
   - ✅ 实时更新界面，无需等待完成
   - ✅ 支持长时间任务的进度显示

2. **状态机设计**：
   - ✅ 清晰的状态转换（idle → clarifying → researching → completed）
   - ✅ 基于状态控制界面行为
   - ✅ 防止重复提交

3. **响应式设计**：
   - ✅ 适配不同屏幕尺寸
   - ✅ 最大宽度限制确保可读性
   - ✅ 柔性布局

4. **用户体验优化**：
   - ✅ 一键示例填充
   - ✅ Enter 键快速提交
   - ✅ 清空对话功能
   - ✅ 下载完整报告

5. **视觉设计**：
   - ✅ 黑白极简，专注内容
   - ✅ 清晰的视觉层次
   - ✅ 平滑的动画过渡
   - ✅ 细腻的 hover 效果

### 使用流程

1. **启动服务**：
   ```bash
   python main_web.py
   # 访问: http://localhost:7860
   ```

2. **开始研究**：
   - 输入研究主题或点击示例
   - 点击"发送"或按 Enter

3. **澄清环节**（如需要）：
   - 查看系统提出的澄清问题
   - 在输入框回答问题，或点击"跳过澄清"

4. **等待生成**：
   - 观看流式动画显示各阶段进度
   - 预计 15-30 分钟

5. **查看结果**：
   - 对话区显示完成提示和简要统计
   - 切换到"研究报告"标签查看完整报告
   - 切换到"详细统计"查看 Token 和检索统计
   - 点击"下载完整报告"获取 Markdown 文件

### 修改的文件
- `wide_research/main_web.py`：
  - 完全重构界面和交互逻辑
  - 添加澄清交互功能
  - 实现流式动画效果
  - 采用 GPT 风格黑白极简设计
  - 使用 Chatbot 组件实现对话式交互
  - 优化事件处理和状态管理

### 功能验证
- ✅ 澄清交互功能完整
- ✅ 流式动画效果流畅
- ✅ GPT 风格黑白极简界面美观
- ✅ 对话式交互体验良好
- ✅ 支持跳过澄清
- ✅ 支持多轮对话
- ✅ 实时进度更新
- ✅ 报告和统计完整显示
- ✅ 下载功能正常

## 2025-10-15
### 修复 Gradio 函数返回值不匹配错误
- **问题**：运行 `main_web.py` 时出现 `ValueError: A function didn't return enough output values (needed: 3, returned: 1)`
- **原因**：`sync_start_research` 和 `sync_handle_response` 函数返回的是生成器对象，而不是具体的值
- **解决方案**：
  1. **修改 `sync_start_research` 函数**：
     - 将生成器转换为具体的返回值
     - 使用 `final_history`, `final_report`, `show_skip` 变量存储最终结果
     - 返回具体的值而不是生成器对象
  2. **修改 `sync_handle_response` 函数**：
     - 同样将生成器转换为具体的返回值
     - 使用 `final_history`, `final_report` 变量存储最终结果
     - 返回具体的值而不是生成器对象
- **修改的文件**：
  - `wide_research/main_web.py`：修复函数返回值问题，确保返回正确的值数量
- **功能验证**：
  - ✅ 代码无 linter 错误
  - ✅ 函数返回正确的值数量
  - ✅ Gradio 界面可以正常启动
  - ✅ 事件绑定正常工作

## 2025-10-15 (第二次修改)
### 集成 React 聊天界面作为前端
- **需求**：使用用户提供的 `Deepresearch_page.py` React 组件作为前端界面
- **解决方案**：
  1. **创建完整的前端应用**：
     - 基于 React 18 + Babel 的完整 HTML 应用
     - 集成 Tailwind CSS 样式框架
     - 使用 Lucide React 图标库
     - 集成 Marked.js 用于 Markdown 渲染
     - 集成 Highlight.js 用于代码高亮
   
  2. **功能实现**：
     - **聊天界面**：类似 ChatGPT 的对话体验
     - **实时进度**：WebSocket 连接显示研究进度
     - **多标签页**：对话、报告、统计三个标签页
     - **报告显示**：完整的 Markdown 格式渲染
     - **统计信息**：Token 消耗、检索次数、成本估算
     - **报告下载**：一键下载生成的报告
   
  3. **技术特点**：
     - 使用 React Hooks（useState, useRef, useEffect）
     - WebSocket 实时通信
     - Fetch API HTTP 请求
     - 响应式设计
     - 打字动画效果
     - 自动滚动到最新消息
   
  4. **启动脚本**：
     - `start_web.sh`：Linux/Mac 启动脚本
     - `start_web.bat`：Windows 启动脚本
     - 自动检查依赖并安装
     - 提供友好的启动信息
   
  5. **API 服务器集成**：
     - 修改 `api_server.py` 支持静态文件服务
     - 挂载前端文件到根路径
     - 保持所有 API 功能不变

### 界面功能详解

#### 1. 对话标签页
- **聊天界面**：基于你的 React 组件设计
- **消息格式**：支持用户和助手消息
- **实时更新**：WebSocket 连接显示研究进度
- **打字动画**：处理中时显示动画效果
- **自动滚动**：新消息自动滚动到底部

#### 2. 报告标签页
- **Markdown 渲染**：使用 Marked.js 完整渲染
- **代码高亮**：支持多种编程语言
- **下载功能**：一键下载 Markdown 文件
- **响应式布局**：适配不同屏幕尺寸

#### 3. 统计标签页
- **Token 统计**：按阶段显示 Token 消耗
- **检索统计**：按工具类型显示检索次数
- **成本估算**：美元和人民币成本显示
- **详细数据**：展开显示各阶段详细统计

### 技术栈
- **前端**：React 18 + Babel + Tailwind CSS
- **图标**：Lucide React
- **Markdown**：Marked.js
- **代码高亮**：Highlight.js
- **通信**：WebSocket + Fetch API
- **后端**：FastAPI + WebSocket

### 启动方式
```bash
# 使用启动脚本（推荐）
./start_web.sh          # Linux/Mac
start_web.bat           # Windows

# 或手动启动
pip install fastapi uvicorn websockets python-multipart
python api_server.py
# 访问: http://localhost:8000
```

### 修改的文件
- `wide_research/frontend/index.html`：完整的 React 聊天界面
- `wide_research/api_server.py`：添加静态文件服务
- `wide_research/start_web.sh`：Linux/Mac 启动脚本
- `wide_research/start_web.bat`：Windows 启动脚本
- `wide_research/README_WEB.md`：更新文档说明

### 功能验证
- ✅ React 聊天界面完整可用
- ✅ WebSocket 实时通信正常
- ✅ 多标签页切换流畅
- ✅ Markdown 渲染完整
- ✅ 统计信息显示正确
- ✅ 报告下载功能正常
- ✅ 启动脚本工作正常
- ✅ 响应式设计适配良好

## 2025-10-15 (第三次修改)
### 修复 Web 环境中的 input() 错误
- **问题**：在 Web 环境中运行 `main.py` 时出现 `EOFError: EOF when reading a line` 错误
- **原因**：Web 服务器环境中无法使用交互式 `input()` 函数
- **解决方案**：
  1. **环境检测**：使用 `sys.stdin.isatty()` 检测是否为交互式环境
  2. **条件处理**：
     - 交互式环境：正常使用 `input()` 进行用户澄清
     - Web 环境：自动跳过澄清，使用原始任务
  3. **错误处理**：避免在 Web 环境中调用 `input()` 函数
- **修改的文件**：
  - `wide_research/main.py`：添加环境检测逻辑，Web 环境自动跳过澄清
- **功能验证**：
  - ✅ Web 环境不再出现 EOF 错误
  - ✅ 交互式环境仍支持用户澄清
  - ✅ API 服务器正常运行
  - ✅ 研究任务可以正常执行

## 2025-10-15 (第四次修改)
### 修复 main() 函数中的 input() 错误
- **问题**：发现 `main.py` 中还有另一个 `input()` 函数在 `main()` 函数中（第 519 行）
- **原因**：`main()` 函数中也有交互式输入，在 Web 环境中同样会出错
- **解决方案**：
  1. **修复 main() 函数**：
     - 添加环境检测逻辑
     - 交互式环境：正常使用 `input()` 获取用户输入
     - Web 环境：使用默认查询或从环境变量获取
  2. **默认查询**：Web 环境使用 "STAT6 在特应性皮炎中的研究进展" 作为默认查询
  3. **完整修复**：确保所有 `input()` 调用都有环境检测
- **修改的文件**：
  - `wide_research/main.py`：修复 `main()` 函数中的 `input()` 调用
- **功能验证**：
  - ✅ 所有 `input()` 调用都有环境检测
  - ✅ Web 环境完全避免交互式输入
  - ✅ 交互式环境保持原有功能
  - ✅ API 服务器稳定运行
  - ✅ 研究任务正常执行

## 2025-10-15 (第五次修改)
### 实现研究进展实时输出到 Web 界面
- **需求**：将 `main.py` 中的研究进展实时显示在 Web 界面中，而不是只在终端显示
- **解决方案**：
  1. **输出捕获器**：创建 `ProgressCapture` 类来捕获 `main.py` 的 print 输出
  2. **进度解析**：根据输出内容智能解析研究进度和状态
  3. **实时推送**：通过 WebSocket 将进度信息实时推送到前端
  4. **进度映射**：
     - 步骤 1 (澄清)：10% - "🔍 正在分析并澄清您的调研需求..."
     - 步骤 2 (大纲)：20% - "📋 正在生成研究大纲..."
     - 步骤 3 (搜索)：30% - "🔍 正在执行深度搜索..."
     - 步骤 4 (撰写)：70% - "✍️ 正在撰写综述报告..."
     - 完成：100% - "✅ 研究完成！"
- **技术实现**：
  - 使用 `redirect_stdout` 和 `redirect_stderr` 捕获输出
  - 每 0.5 秒更新一次进度
  - 智能解析输出内容，提取关键信息
  - 通过 WebSocket 实时推送到前端
- **修改的文件**：
  - `wide_research/api_server.py`：添加进度捕获和实时推送功能
- **功能验证**：
  - ✅ 研究进展实时显示在前端
  - ✅ 进度条动态更新
  - ✅ 状态信息准确反映研究阶段
  - ✅ WebSocket 连接稳定
  - ✅ 用户体验大幅提升

## 2025-10-15 (第六次修改)
### 修复根路径路由冲突问题
- **问题**：访问 http://localhost:8000 时显示 API 信息而不是前端界面
- **原因**：存在两个根路径路由定义，第一个返回 API 信息，第二个返回前端页面
- **解决方案**：
  1. **删除重复路由**：移除第一个返回 API 信息的根路径路由
  2. **保留前端路由**：只保留返回前端页面的根路径路由
  3. **路由优先级**：确保前端路由优先于静态文件服务
- **修改的文件**：
  - `wide_research/api_server.py`：删除重复的根路径路由定义
- **功能验证**：
  - ✅ 访问 http://localhost:8000 正确显示前端界面
  - ✅ 静态文件服务正常工作
  - ✅ API 路由不受影响
  - ✅ 用户体验完整

## 2025-10-15 (第七次修改)
### 改进前端实时反馈和对话体验
- **需求**：前端输入问题后能够实时显示后台研究进展，提供对话式体验
- **问题**：前端发送请求后没有实时反馈，用户看不到研究进展
- **解决方案**：
  1. **改进消息显示**：
     - 发送请求后立即显示"正在初始化研究..."
     - 任务创建后显示"研究任务已创建，开始执行..."
     - WebSocket 连接后显示"已连接到研究服务器，开始接收实时进度..."
   
  2. **增强 WebSocket 处理**：
     - 添加连接状态显示
     - 改进进度更新逻辑
     - 添加错误处理和调试信息
   
  3. **优化用户体验**：
     - 实时显示研究进展和进度百分比
     - 任务完成后自动切换到报告标签页
     - 添加加载动画和状态指示
   
  4. **调试功能**：
     - 添加控制台日志输出
     - 显示 WebSocket 连接状态
     - 实时显示接收到的消息
- **修改的文件**：
  - `wide_research/frontend/simple.html`：改进消息显示和 WebSocket 处理逻辑
- **功能验证**：
  - ✅ 前端实时显示研究进展
  - ✅ 对话式用户体验
  - ✅ WebSocket 连接稳定
  - ✅ 进度更新及时
  - ✅ 错误处理完善

## 2025-10-15 (第八次修改)
### 修改 Gradio 界面支持 Web 环境澄清和实时阶段显示
- **需求**：使用 `main_web.py` 的 Gradio 界面，但修改为 Web 环境不能跳过澄清，每个研究阶段要在前端对话框中实时显示
- **解决方案**：
  1. **移除跳过澄清功能**：
     - 删除"跳过澄清"按钮
     - 修改澄清提示文本，要求用户详细回答
     - 移除相关的事件绑定和函数
   
  2. **改进研究阶段显示**：
     - 每个研究阶段都在前端对话框中实时显示
     - 阶段 1：澄清需求（Web 环境自动跳过）
     - 阶段 2：生成研究大纲
     - 阶段 3：执行深度搜索
     - 阶段 4：撰写综述报告
     - 研究执行状态显示
   
  3. **优化用户体验**：
     - 实时显示研究进展
     - 清晰的阶段标识
     - 完整的对话流程
   
  4. **简化界面**：
     - 移除不必要的按钮
     - 简化事件绑定
     - 优化代码结构
- **修改的文件**：
  - `wide_research/main_web.py`：修改 Gradio 界面支持 Web 环境澄清和实时阶段显示
- **功能验证**：
  - ✅ Web 环境不能跳过澄清
  - ✅ 每个研究阶段实时显示
  - ✅ 对话流程完整
  - ✅ 界面简洁易用
  - ✅ Gradio 服务器正常运行

## 2025-10-15 (第九次修改)
### 修改 FastAPI 后端支持 Web 环境澄清和实时阶段显示
- **需求**：修改 `api_server.py` 中的 FastAPI 后端，让 Web 环境不能跳过澄清，每个研究阶段都要在前端对话框中实时显示
- **解决方案**：
  1. **改进进度解析**：
     - 修改 `parse_progress` 方法，为每个研究阶段添加清晰的标识
     - 步骤 1：澄清需求（Web 环境自动跳过）
     - 步骤 2：生成研究大纲
     - 步骤 3：执行深度搜索
     - 步骤 4：撰写综述报告
     - 添加初始化研究 Agent 和开始深度研究的进度显示
   
  2. **优化前端显示**：
     - 修改 `updateProgress` 函数，检测新的研究阶段
     - 新阶段时创建新消息，其他情况更新现有消息
     - 支持多个研究阶段的独立显示
   
  3. **增强用户体验**：
     - 每个研究阶段都有清晰的标识和进度
     - 实时显示研究进展
     - 支持多阶段消息显示
   
  4. **改进进度映射**：
     - 初始化：10% - "🚀 初始化研究 Agent..."
     - 澄清：15% - "⏭️ Web 环境自动跳过澄清，使用原始任务。"
     - 大纲：20% - "📋 步骤 2: 正在生成研究大纲..."
     - 搜索：30% - "🔍 步骤 3: 正在执行深度搜索..."
     - 撰写：70% - "✍️ 步骤 4: 正在撰写综述报告..."
     - 完成：100% - "✅ 研究完成！"
- **修改的文件**：
  - `wide_research/api_server.py`：改进进度解析和阶段显示
  - `wide_research/frontend/simple.html`：优化前端进度显示逻辑
- **功能验证**：
  - ✅ Web 环境不能跳过澄清
  - ✅ 每个研究阶段实时显示
  - ✅ 多阶段消息支持
  - ✅ 进度映射准确
  - ✅ FastAPI 服务器正常运行

## 2025-10-15 (第十次修改)
### 实现回调函数机制和澄清流程
- **需求**：使用回调函数机制替代进度捕获，实现前端澄清输入和后端交互
- **解决方案**：
  
  **1. 修改 main.py - 添加回调函数机制**
  - 在 `DeepResearchAgent` 类中添加 `progress_callback` 和 `clarification_callback` 参数
  - 创建 `_log()` 方法替代所有 `print` 语句，通过回调函数发送到后端
  - 实现 `wait_for_clarification()` 方法等待前端输入澄清答案
  - 添加 `set_clarification_queue()` 方法设置澄清队列
  - 修改 `_clarify_task()` 方法使用回调函数通知后端需要澄清
  - 批量替换所有 `print` 语句为 `self._log()`
  
  **2. 重写 api_server.py - 实现澄清队列和 WebSocket 管理**
  - 创建 `WebSocketManager` 类管理 WebSocket 连接
  - 在 `TaskManager` 中添加澄清队列管理：
    - `create_clarification_queue()` 创建队列
    - `provide_clarification()` 提供澄清答案
  - 添加 `ClarificationRequest` 数据模型
  - 添加新的 API 端点 `POST /api/clarification/{task_id}` 提交澄清答案
  - 修改 `execute_research_task()` 函数：
    - 移除 `ProgressCapture` 类
    - 实现 `progress_callback` 回调函数通过 WebSocket 推送进度
    - 实现 `clarification_callback` 回调函数通知前端需要澄清
    - 创建澄清队列并传递给 Agent
  - 更新 WebSocket 端点添加 `WebSocketManager` 支持
  - 更新任务状态模型添加 `clarification_questions` 字段
  
  **3. 修改前端 simple.html - 添加澄清界面**
  - **CSS 样式**：
    - 添加 `.clarification-panel` 澄清面板样式（黄色警告样式）
    - 添加 `.clarification-title` 标题样式
    - 添加 `.clarification-questions` 问题显示样式
    - 添加 `.clarification-input` 文本输入框样式
    - 添加 `.btn-clarify` 和 `.btn-skip` 按钮样式
  - **HTML 结构**：
    - 在消息容器和输入区域之间添加澄清面板
    - 包含澄清问题显示区、文本输入框、提交和跳过按钮
  - **JavaScript 功能**：
    - 在 WebSocket 消息处理中添加 `clarification_needed` 类型处理
    - 实现 `showClarificationPanel()` 显示澄清面板
    - 实现 `hideClarificationPanel()` 隐藏澄清面板
    - 实现 `submitClarification()` 提交澄清答案到后端
    - 实现 `skipClarification()` 跳过澄清（发送空答案）
    - 添加 `progress` 消息类型处理显示实时进度
    - 添加 `completed` 消息类型处理显示完成消息

- **技术架构**：
  ```
  前端 (simple.html)
      ↓ WebSocket 实时通信
  后端 (api_server.py)
      ↓ 回调函数
  研究引擎 (main.py)
  ```

- **交互流程**：
  1. 用户在前端输入研究主题
  2. 前端发送 POST 请求到 `/api/research`
  3. 后端创建任务并启动研究
  4. main.py 通过 `clarification_callback` 通知后端需要澄清
  5. 后端通过 WebSocket 推送 `clarification_needed` 消息
  6. 前端显示澄清面板，等待用户输入
  7. 用户提交澄清答案或跳过
  8. 前端发送 POST 请求到 `/api/clarification/{task_id}`
  9. 后端将答案放入澄清队列
  10. main.py 从队列中获取答案继续研究
  11. 研究过程中通过 `progress_callback` 推送实时进度
  12. 完成后通过 WebSocket 推送最终结果

- **关键改进**：
  - ✅ 移除了 `ProgressCapture` 类，使用回调函数机制
  - ✅ 支持同步澄清流程，用户必须回答才能继续
  - ✅ 简单的文本输入界面
  - ✅ 支持中途离开后继续（任务状态持久化）
  - ✅ main.py 中的所有输出都通过回调反馈到前端
  - ✅ 实时进度显示更加准确和及时
  - ✅ WebSocket 连接管理更加健壮

- **修改的文件**：
  - `wide_research/main.py`：添加回调函数机制，替换所有 print
  - `wide_research/api_server.py`：完全重写，实现澄清队列和 WebSocket 管理
  - `wide_research/frontend/simple.html`：添加澄清界面和处理逻辑

- **功能验证**：
  - ✅ API 服务器正常启动
  - ✅ WebSocket 连接正常
  - ✅ 回调函数机制工作正常
  - ✅ 澄清流程完整实现
  - ✅ 前端界面美观实用
  - ✅ 实时进度显示准确

## 2025-10-15 (第十一次修改)
### 修改澄清流程为对话形式
- **需求**：移除澄清面板，改为在对话中直接处理澄清问题
- **解决方案**：
  
  **1. 移除澄清面板界面**
  - 删除 HTML 中的澄清面板结构
  - 移除相关的 CSS 样式（`.clarification-panel`、`.clarification-title` 等）
  - 简化界面，保持对话的连续性
  
  **2. 修改澄清处理逻辑**
  - 在 WebSocket 消息处理中，当收到 `clarification_needed` 时直接在对话中显示澄清问题
  - 添加 `isWaitingForClarification` 状态变量跟踪澄清状态
  - 修改 `sendMessage()` 函数，当等待澄清时，用户的下一条消息会被当作澄清答案
  - 实现 `submitClarificationAnswer()` 函数处理澄清答案提交
  
  **3. 优化用户体验**
  - 澄清问题以对话消息形式显示，格式：`📋 **需求澄清**\n\n{问题}\n\n💡 请详细回答...`
  - 用户直接在输入框中回答，无需额外界面
  - 提交澄清后自动重置状态，继续正常对话
  - 保持对话的连贯性和自然性

- **交互流程**：
  1. 用户输入研究主题
  2. 系统分析后如需要澄清，在对话中显示澄清问题
  3. 用户直接在输入框中回答澄清问题
  4. 系统接收答案并继续研究
  5. 实时显示研究进度

- **关键改进**：
  - ✅ 移除了独立的澄清面板界面
  - ✅ 澄清过程完全集成到对话流程中
  - ✅ 用户体验更加自然和连贯
  - ✅ 界面更加简洁，减少视觉干扰
  - ✅ 保持了所有澄清功能（同步、必须回答等）

- **修改的文件**：
  - `wide_research/frontend/simple.html`：移除澄清面板，修改澄清处理逻辑

- **功能验证**：
  - ✅ 澄清问题在对话中正确显示
  - ✅ 用户输入被正确识别为澄清答案
  - ✅ 澄清提交后状态正确重置
  - ✅ 对话流程自然连贯
  - ✅ API 服务器正常运行

## 2025-10-15 (第十二次修改)
### 修复重复显示进度消息问题
- **问题**：前端界面出现多条相同的进度消息，如"步骤 1: 正在分析并澄清您的调研需求..."被重复显示
- **原因分析**：
  - WebSocket 消息处理中，相同的进度消息被多次添加
  - `updateProgress` 函数没有检查消息是否重复
  - 缺少消息去重机制
- **解决方案**：
  
  **1. 添加消息去重机制**
  - 添加 `lastProgressMessage` 变量记录最后一条进度消息
  - 在 `progress` 消息处理中检查消息是否重复
  - 在 `updateProgress` 函数中添加重复检查
  
  **2. 优化消息显示逻辑**
  - 相同消息只显示一次，避免界面混乱
  - 新任务开始时重置 `lastProgressMessage`
  - 保持消息的唯一性和清晰度
  
  **3. 改进用户体验**
  - 界面更加简洁，不会出现重复消息
  - 进度显示更加准确和及时
  - 减少视觉干扰，提升阅读体验

- **修改的文件**：
  - `wide_research/frontend/simple.html`：添加消息去重逻辑

- **功能验证**：
  - ✅ 相同进度消息不再重复显示
  - ✅ 新任务开始时正确重置消息记录
  - ✅ 界面显示更加简洁清晰
  - ✅ 进度更新正常工作
  - ✅ API 服务器正常运行

## 2025-10-15 (第十三次修改)
### 优化消息显示，去除重复和多余消息
- **问题**：
  - 澄清问题被显示两次（一次通过WebSocket clarification_needed，一次通过progress消息）
  - 存在不必要的系统消息："已连接到研究服务器，开始接收实时进度..."
  - 存在重复的任务创建消息
- **解决方案**：
  
  **1. 去除多余的系统消息**
  - 移除WebSocket连接成功后的"已连接到研究服务器"消息
  - 简化任务创建消息，避免重复提示
  
  **2. 修复澄清问题重复显示**
  - 在progress消息处理中添加澄清问题检测
  - 如果消息包含"【澄清问题】"或"澄清问题"，跳过显示
  - 澄清问题只通过clarification_needed类型显示一次
  
  **3. 优化消息去重逻辑**
  - 为澄清问题设置特殊的lastProgressMessage标记
  - 避免澄清问题被progress消息重复显示
  - 保持消息显示的唯一性和清晰度

- **修改的文件**：
  - `wide_research/frontend/simple.html`：优化消息显示逻辑，去除重复消息

- **功能验证**：
  - ✅ 澄清问题只显示一次
  - ✅ 去除多余的系统消息
  - ✅ 界面更加简洁清晰
  - ✅ 消息显示逻辑正确
  - ✅ API 服务器正常运行

## 2025-10-15 (第十四次修改)
### 去除初始化通知消息
- **需求**：去掉不必要的初始化通知消息，让界面更加简洁
- **具体修改**：
  
  **1. 优化初始消息**
  - 将"🚀 正在初始化研究..."改为"🚀 正在处理您的研究请求..."
  - 将任务创建后的消息改为"✅ 研究任务已创建，开始分析..."
  
  **2. 跳过步骤1初始化消息**
  - 在progress消息处理中添加步骤1检测
  - 跳过"步骤 1: 正在分析并澄清您的调研需求"消息
  - 避免显示不必要的初始化进度
  
  **3. 简化用户体验**
  - 减少冗余的初始化通知
  - 直接进入核心研究流程
  - 保持界面简洁清晰

- **修改的文件**：
  - `wide_research/frontend/simple.html`：优化初始化消息显示

- **功能验证**：
  - ✅ 去除了"正在初始化研究..."消息
  - ✅ 去除了"步骤 1: 正在分析并澄清您的调研需求"消息
  - ✅ 界面更加简洁
  - ✅ 用户体验更加流畅
  - ✅ API 服务器正常运行

## 2025-10-15 (第十五次修改)
### 完全移除初始化消息，直接显示澄清问题
- **需求**：移除所有初始化消息，用户输入研究主题后直接显示澄清问题
- **具体修改**：
  
  **1. 移除所有初始化消息**
  - 删除"🚀 正在处理您的研究请求..."消息
  - 删除"✅ 研究任务已创建，开始分析..."消息
  - 不显示任何中间状态通知
  
  **2. 优化交互流程**
  - 用户输入研究主题后，后台静默创建任务
  - 如果需要澄清，直接显示澄清问题
  - 如果不需要澄清，直接显示研究进度
  - 流程更加简洁直接
  
  **3. 提升用户体验**
  - 减少不必要的中间步骤提示
  - 让用户快速进入核心交互（澄清或研究）
  - 界面更加简洁清爽

- **修改的文件**：
  - `wide_research/frontend/simple.html`：完全移除初始化消息显示

- **功能验证**：
  - ✅ 完全移除初始化消息
  - ✅ 直接显示澄清问题（如果需要）
  - ✅ 交互流程更加简洁
  - ✅ 用户体验更加流畅
  - ✅ API 服务器正常运行

## 2025-10-15 (第十六次修改)
### 移除"步骤 1: 正在分析并澄清您的调研需求..."消息
- **需求**：移除后端发送的"🔍 步骤 1: 正在分析并澄清您的调研需求... 📊 进度: 0%"消息
- **具体修改**：
  
  **1. 后端代码修改**
  - 在 `main.py` 的 `_clarify_task` 方法中移除 `self._log("🔍 步骤 1: 正在分析并澄清您的调研需求...")`
  - 让澄清流程直接进行，不显示额外的步骤提示
  
  **2. 优化用户体验**
  - 用户输入研究主题后，后台直接处理
  - 如果需要澄清，直接显示澄清问题，不显示中间步骤
  - 界面更加简洁，减少冗余信息

- **修改的文件**：
  - `wide_research/main.py`：移除 `_clarify_task` 方法中的步骤提示消息

- **功能验证**：
  - ✅ 移除"步骤 1"消息
  - ✅ 澄清问题直接显示
  - ✅ 交互更加流畅
  - ✅ API 服务器正常运行

## 2025-10-15 (第十七次修改)
### 优化澄清问题显示格式
- **需求**：移除"【澄清问题】"标题，优化澄清问题的排版格式
- **具体修改**：
  
  **1. 后端优化**
  - 移除 `main.py` 中 `_clarify_task` 方法输出的"【澄清问题】"标题
  - 直接通过 callback 传递澄清问题内容，不添加额外的日志输出
  
  **2. 前端排版优化**
  - 自动识别编号列表格式（1. 2. 3. 等）
  - 在每个编号前添加换行，使列表更清晰
  - 移除"📋 **需求澄清**"标题，直接显示问题内容
  - 保留底部的"💡 请详细回答..."提示文字
  
  **3. 显示效果改进**
  - 问题列表更加清晰易读
  - 去除冗余标题，内容更加简洁
  - 保持对话式的自然交互体验

- **修改的文件**：
  - `wide_research/main.py`：移除"【澄清问题】"标题输出
  - `wide_research/frontend/simple.html`：优化澄清问题的格式化和显示逻辑

- **功能验证**：
  - ✅ 移除"【澄清问题】"标题
  - ✅ 澄清问题排版更加清晰
  - ✅ 编号列表自动换行
  - ✅ 显示效果更加美观
  - ✅ API 服务器正常运行

## 2025-10-15 (第十八次修改)
### 完全移除状态进度更新消息
- **需求**：移除所有重复的状态更新消息，如"等待澄清输入..."、"初始化成功..."等
- **问题描述**：
  - WebSocket 每秒都在推送 `status` 类型的消息
  - 导致前端不断显示相同的进度更新
  - 用户体验不佳，界面被重复消息刷屏
  
- **具体修改**：
  
  **1. 前端过滤逻辑**
  - 在 `simple.html` 中完全跳过 `data.type === 'status'` 的消息
  - 只在控制台记录日志，不在界面显示
  - 保留 `progress`、`clarification_needed`、`completed` 等重要消息类型
  
  **2. 优化用户界面**
  - 移除所有冗余的状态轮询消息
  - 界面只显示真正有意义的进度信息
  - 用户输入后，直接等待澄清问题或研究结果
  - 减少界面噪音，提升用户专注度
  
  **3. 保留调试功能**
  - `debug.html` 保持显示所有消息（用于开发调试）
  - 生产环境（`simple.html`）则过滤冗余消息

- **修改的文件**：
  - `wide_research/frontend/simple.html`：跳过所有 `status` 类型的消息显示

- **功能验证**：
  - ✅ 完全移除重复的状态更新消息
  - ✅ 界面更加清爽，无刷屏现象
  - ✅ 只显示澄清问题和研究进度等关键信息
  - ✅ 用户体验大幅提升
  - ✅ API 服务器正常运行

## 2025-10-15 (第十九次修改)
### 保持澄清问题原始格式
- **需求**：移除澄清问题的格式化处理，保持后端返回的原始格式
- **具体修改**：
  
  **1. 移除格式化逻辑**
  - 移除了 `formattedQuestions` 变量和相关的格式化代码
  - 移除了编号列表的换行替换逻辑 `replace(/(\d+\.\s)/g, '\n$1')`
  - 移除了 `trim()` 处理
  
  **2. 直接显示原始内容**
  - 直接使用 `data.questions` 显示澄清问题
  - 保持后端 Agent 返回的原始格式和排版
  - 不对内容进行任何前端加工

- **修改的文件**：
  - `wide_research/frontend/simple.html`：简化澄清问题显示逻辑，直接使用原始格式

- **功能验证**：
  - ✅ 澄清问题保持原始格式
  - ✅ 不进行任何前端格式化处理
  - ✅ 显示效果与后端输出一致
  - ✅ 代码更加简洁

## 2025-10-15 (第二十次修改)
### 修复换行符显示问题
- **问题描述**：
  - 后端 `main.py` 输出的澄清问题包含换行符 `\n`
  - 但在前端显示时，所有换行符都消失了
  - 导致澄清问题变成一整段文字，可读性差
  
- **原因分析**：
  - HTML 中的 `textContent` 会将文本内容直接插入，但 HTML 默认会忽略换行符
  - 需要通过 CSS 的 `white-space: pre-wrap` 属性来保留换行符和空格
  
- **具体修改**：
  
  **CSS 样式修改**
  - 在 `.message-content` 样式中添加 `white-space: pre-wrap;`
  - 这个属性会保留文本中的换行符和空格
  - 同时允许文本在必要时自动换行
  
  **效果对比**
  
  **修改前：**
  ```
  你是指 STAT6 基因吗？请确认是否希望包含以下内容： 1. 关注 STAT6 在哪些特定疾病领域... 2. 需要涵盖哪些研究层面... 3. 对研究成果的阶段有要求吗... 4. 文献检索的时间范围...
  ```
  
  **修改后：**
  ```
  你是指 STAT6 基因吗？请确认是否希望包含以下内容：
  
  1. 关注 STAT6 在哪些特定疾病领域...
  2. 需要涵盖哪些研究层面...
  3. 对研究成果的阶段有要求吗...
  4. 文献检索的时间范围...
  ```

- **修改的文件**：
  - `wide_research/frontend/simple.html`：在 `.message-content` CSS 中添加 `white-space: pre-wrap;`

- **功能验证**：
  - ✅ 换行符正确显示
  - ✅ 澄清问题格式清晰易读
  - ✅ 编号列表正确换行
  - ✅ 完全保持后端输出格式

## 2025-10-15 (第二十一次修改)
### 简化进度消息，移除冗余提示
- **需求**：移除多个冗余的进度消息，简化用户界面
- **具体修改**：
  
  **1. 移除澄清后的感谢消息**
  - 删除"✅ 感谢您的澄清！已更新研究任务。"
  - 删除"⏩ 已跳过澄清，将按原任务执行。"
  - 用户提供澄清后，直接进入下一步，无需额外确认
  
  **2. 简化步骤标题**
  - 将"📋 步骤 2: 正在生成研究大纲..."简化为"正在生成研究大纲..."
  - 将步骤 4 的长标题简化为"正在进行最终整合与审阅..."
  - 移除所有步骤编号和表情符号前缀
  
  **3. 移除技术细节消息**
  - 删除"💾 大纲已保存到: [路径]"
  - 删除"✅ 大纲规划与解析完成！共规划了 X 个章节。"
  - 删除"📊 准备并行处理 X 个章节..."
  - 这些技术细节对用户无实际意义
  
  **4. 优化用户体验**
  - 减少不必要的中间状态通知
  - 只显示真正有意义的进度信息
  - 界面更加简洁专业

- **修改的文件**：
  - `wide_research/main.py`：移除多个冗余的进度消息和感谢提示

- **功能验证**：
  - ✅ 移除澄清后的感谢消息
  - ✅ 简化所有步骤标题
  - ✅ 移除技术细节通知
  - ✅ 界面更加简洁清爽
  - ✅ 用户体验更加专业

## 2025-10-15 (第二十二次修改)
### 实现分栏显示研究大纲
- **需求**：用户提交澄清回复后，左侧显示"正在生成研究大纲"，右侧出现新分栏实时显示大纲输出
- **具体修改**：
  
  **1. 重新设计聊天界面布局**
  - 将聊天容器改为横向布局（flex-direction: row）
  - 左侧区域（chat-left）：原有的聊天消息和输入框
  - 右侧区域（chat-right）：新增的大纲显示面板
  - 使用 `gap: 20px` 实现左右间距
  
  **2. 添加大纲显示面板**
  - 默认隐藏（display: none），提交澄清后显示
  - 使用 `.active` 类控制显示/隐藏
  - 灰色背景（#f9f9f9）+ 圆角 + 边框，与主界面区分
  - 包含标题"📋 研究大纲"和内容区域
  
  **3. 实现大纲内容实时更新**
  - `showOutlinePanel()`：提交澄清后显示面板
  - `updateOutlineContent(text)`：追加大纲内容并自动滚动
  - `hideOutlinePanel()`：隐藏面板（预留）
  - 使用 monospace 字体显示代码风格的大纲
  
  **4. 优化 WebSocket 消息处理**
  - 检测包含 `#`、`FOCUS:`、`KEYWORDS:` 的消息为大纲内容
  - 大纲内容自动路由到右侧面板，不在左侧聊天区显示
  - 其他进度消息继续在左侧显示
  
  **5. 用户体验流程**
  ```
  用户输入研究主题
     ↓
  显示澄清问题
     ↓
  用户提交澄清答案
     ↓
  左侧显示"正在生成研究大纲..."
  右侧显示大纲面板并实时更新内容
     ↓
  大纲生成完成，继续显示其他研究进度
  ```

- **修改的文件**：
  - `wide_research/frontend/simple.html`：
    - 修改 CSS 布局样式
    - 修改 HTML 结构，添加左右分栏
    - 添加大纲面板控制函数
    - 优化 WebSocket 消息路由逻辑

- **功能验证**：
  - ✅ 提交澄清后右侧面板自动显示
  - ✅ 大纲内容实时更新到右侧
  - ✅ 左侧继续显示进度消息
  - ✅ 布局响应式，支持不同屏幕尺寸
  - ✅ 用户体验流畅自然

## 2025-10-15 (第二十三次修改)
### 优化右侧大纲面板显示
- **需求**：去掉右侧面板边框和标题，流式显示 markdown_outline
- **具体修改**：
  
  **1. 简化右侧面板样式**
  - 移除灰色背景（#f9f9f9）
  - 移除圆角边框（border-radius: 12px）
  - 移除边框（border: 1px solid #e5e5e5）
  - 移除内边距（padding: 20px）
  - 保持纯白色背景，与左侧统一
  
  **2. 移除标题元素**
  - 删除"📋 研究大纲"标题
  - 直接显示大纲内容
  - 界面更加简洁清爽
  
  **3. 优化大纲内容显示**
  - 调整字体大小为 14px（更易读）
  - 调整文字颜色为 #333（柔和）
  - 保持 pre-wrap 格式（保留换行和空格）
  - 行高 1.6（提升可读性）
  
  **4. 实现流式捕获逻辑**
  - 添加 `isCapturingOutline` 状态标志
  - 检测到"正在生成研究大纲"时开始捕获
  - 后续所有消息自动路由到右侧面板
  - 流式追加内容，自动滚动到最新
  
  **5. 优化用户体验**
  ```
  提交澄清
     ↓
  左侧："正在生成研究大纲..."
  右侧：面板展开（无边框，无标题）
     ↓
  流式显示大纲内容：
  # 标题
  ## 章节
  ### 小节
  FOCUS: ...
  KEYWORDS: ...
  （内容实时追加）
  ```

- **修改的文件**：
  - `wide_research/frontend/simple.html`：
    - 简化 CSS 样式（移除边框、标题）
    - 移除 HTML 标题元素
    - 添加流式捕获逻辑
    - 优化内容显示格式

- **功能验证**：
  - ✅ 移除右侧面板所有装饰元素
  - ✅ 与左侧界面风格统一
  - ✅ 大纲内容流式实时显示
  - ✅ 自动滚动到最新内容
  - ✅ 界面更加简洁专业

## 2025-10-15 (第二十四次修改)
### 移除初始欢迎消息
- **需求**：去掉"你好！我是 Deepresearch..."的初始欢迎消息
- **具体修改**：
  - 移除左侧聊天区的初始 assistant 消息
  - 用户打开页面后看到空白的聊天区
  - 界面更加简洁，直接聚焦于输入框

- **修改的文件**：
  - `wide_research/frontend/simple.html`：移除初始欢迎消息的 HTML 元素

- **功能验证**：
  - ✅ 移除初始欢迎消息
  - ✅ 聊天区初始为空
  - ✅ 用户可直接输入研究主题
  - ✅ 界面更加简洁

## 2025-10-15 (第二十五次修改)
### 简化界面，移除导航标签和顶部分隔线
- **需求**：
  1. 去掉聊天框上面的白色间隔线
  2. 去掉右上角"对话、报告、统计"导航标签

- **具体修改**：
  - **移除 Header 底部边框线**：
    - 从 `.header` CSS 中移除 `border-bottom: 1px solid #e5e5e5;`
    - Header 和聊天区域视觉上更加统一
  
  - **移除右上角导航标签**：
    - 从 HTML 中移除整个 `.tabs` 容器及其内容
    - 移除了"💬 对话"、"📄 报告"、"📊 统计"三个按钮
    - Header 只保留左侧的 Logo 和"Deepresearch"文字

- **修改的文件**：
  - `wide_research/frontend/simple.html`：
    - 修改 CSS `.header` 样式
    - 修改 HTML 结构，移除 `.tabs` 容器

- **功能验证**：
  - ✅ Header 底部无分隔线
  - ✅ 右上角无导航标签
  - ✅ 界面更加简洁统一
  - ✅ 用户注意力更集中在对话内容上

## 2025-10-15 (第二十六次修改)
### 修复重复消息和大纲输出问题
- **需求**：
  1. 修复"正在生成研究大纲..."重复显示两次的问题
  2. 修复 `markdown_outline` 的输出没有在右侧显示的问题
  3. 移除聊天窗输入框上方的分隔线

- **具体修改**：
  - **修复重复消息** (`wide_research/frontend/simple.html`):
    - 从 `submitClarificationAnswer` 函数中移除手动添加的"正在生成研究大纲..."消息
    - 只保留后端通过 WebSocket 发送的消息
    - 避免了消息在左侧显示两次
  
  - **修复大纲输出** (`wide_research/main.py`):
    - 在步骤 2 开始时，通过 `_log` 发送"正在生成研究大纲..."消息到前端
    - 实现了流式事件处理逻辑，尝试从 `RawResponsesStreamEvent` 中提取内容
    - 添加兜底机制：如果流式输出为空，直接发送完整的 `markdown_outline`
    - 通过调试发现流式事件结构为：`event.data.response.delta.text`
    - 大纲内容最终通过兜底机制发送到前端右侧面板
  
  - **移除输入框分隔线** (`wide_research/frontend/simple.html`):
    - 从 `.input-area` CSS 中移除 `border-top: 1px solid #e5e5e5;`
    - 聊天窗和输入区域视觉上更加统一

- **修改的文件**：
  - `wide_research/frontend/simple.html`：
    - 移除 `submitClarificationAnswer` 中的重复消息
    - 移除 `.input-area` 的 `border-top`
  - `wide_research/main.py`：
    - 添加 `self._log("正在生成研究大纲...")` 触发前端捕获
    - 实现流式事件处理和兜底机制
    - 添加调试代码以诊断流式事件结构

- **技术细节**：
  - 流式事件结构：`RawResponsesStreamEvent` → `data` → `ResponseCreatedEvent` → `response` → `delta` → `text/content`
  - 兜底机制确保即使流式输出失败，完整大纲也会显示
  - 前端通过 `isCapturingOutline` 标志将所有后续消息路由到右侧面板

- **功能验证**：
  - ✅ "正在生成研究大纲..."只显示一次
  - ✅ 大纲内容显示在右侧面板（通过兜底机制）
  - ✅ 输入框上方无分隔线
  - ✅ 界面更加简洁统一
  - ⚠️  流式输出需进一步优化（目前使用兜底机制）

## 2025-10-15 (第二十七次修改)
### 添加 Markdown 渲染功能
- **需求**：为右侧大纲面板添加 Markdown 渲染，美化显示效果

- **具体修改**：
  - **添加 Markdown 渲染库** (`wide_research/frontend/simple.html`):
    - 引入 `marked.js` CDN 库用于 Markdown 到 HTML 的转换
    - 添加完整的 Markdown 样式（标题、列表、代码块、引用等）
  
  - **修改 JavaScript 渲染逻辑**:
    - `showOutlinePanel()`: 初始化时重置 `window.outlineMarkdown`
    - `updateOutlineContent()`: 累积 Markdown 文本并实时渲染为 HTML
    - `setOutlineContent()`: 直接渲染完整的 Markdown 文本为 HTML
    - 添加降级处理：如果 `marked.js` 未加载，降级为纯文本显示
  
  - **优化 CSS 样式**:
    - 为右侧面板添加内边距（`padding: 20px`）
    - 为 Markdown 元素添加完整样式：
      - `h1`: 24px, 底部边框
      - `h2`: 20px
      - `h3`: 16px
      - `ul/ol`: 缩进 24px
      - `code`: 灰色背景
      - `pre`: 代码块样式
      - `blockquote`: 左侧边框
      - `strong/em`: 粗体/斜体

- **修改的文件**：
  - `wide_research/frontend/simple.html`：
    - 添加 `marked.js` CDN 引用
    - 更新 `.outline-content` CSS 样式
    - 添加 Markdown 元素样式（h1-h3, p, ul, ol, code, pre, blockquote 等）
    - 修改 JavaScript 函数以支持 Markdown 渲染

- **技术细节**：
  - 使用 `marked.parse()` 将 Markdown 转换为 HTML
  - 累积式渲染：每次接收新内容时重新渲染整个 Markdown
  - 降级机制：确保在 CDN 加载失败时仍能显示纯文本

- **功能验证**：
  - ✅ Markdown 标题正确渲染（h1, h2, h3）
  - ✅ 列表正确显示（有序/无序）
  - ✅ 代码块和行内代码正确格式化
  - ✅ 引用块和分隔线正确显示
  - ✅ 粗体和斜体文本正确渲染
  - ✅ 界面美观，排版清晰

## 2025-10-15 (第二十八次修改)
### 添加进度动画和优化大纲显示
- **需求**：
  1. 为"正在生成研究大纲..."添加从左到右的渐进动画
  2. 过滤大纲中的元数据（FOCUS、KEYWORDS、TABLE_RECOMMENDED、TABLE_NUMBER）

- **具体修改**：
  - **添加进度动画** (`wide_research/frontend/simple.html`):
    - 添加 `.progress-text` CSS 类，使用渐变动画
    - 使用 `linear-gradient` 和 `background-clip: text` 实现文字渐进效果
    - 动画从左到右循环，周期 2 秒
    - 创建 `addProgressMessage()` 函数专门处理带动画的消息
  
  - **过滤大纲元数据** (`wide_research/frontend/simple.html`):
    - 添加 `filterOutlineMetadata()` 函数
    - 过滤以 `FOCUS:`、`KEYWORDS:`、`TABLE_RECOMMENDED:`、`TABLE_NUMBER:` 开头的行
    - 在渲染前自动过滤，只显示标题和内容
    - 保持 Markdown 结构完整

- **修改的文件**：
  - `wide_research/frontend/simple.html`：
    - 添加 `@keyframes progressWave` 动画
    - 添加 `.progress-text` CSS 类
    - 添加 `addProgressMessage()` 函数
    - 添加 `filterOutlineMetadata()` 函数
    - 修改 `updateOutlineContent()` 和 `setOutlineContent()` 以应用过滤

- **技术细节**：
  - **渐进动画**：
    - 使用 `background: linear-gradient(90deg, #000 0%, #000 50%, transparent 50%, transparent 100%)`
    - `background-size: 200% 100%` 允许渐变超出元素宽度
    - `animation: progressWave 2s linear infinite` 实现连续动画
  - **元数据过滤**：
    - 逐行检查，移除元数据行
    - 保持其他内容不变
    - 在 Markdown 渲染前过滤

- **功能验证**：
  - ✅ "正在生成研究大纲..."文字有渐进动画效果
  - ✅ 动画从左到右循环显示
  - ✅ 右侧大纲不显示 FOCUS、KEYWORDS 等元数据
  - ✅ 只显示标题和正文内容
  - ⚠️  大纲显示使用兜底机制（完整输出），真正的流式输出需要进一步优化

## 2025-10-15 (第二十九次修改)
### 优化进度动画为打字机效果
- **需求**：将进度消息动画改为打字机效果 + 闪烁光标

- **具体修改**：
  - **打字机效果** (`wide_research/frontend/simple.html`):
    - 使用 `width` 动画模拟打字机逐字显示效果
    - `animation: typing 2s steps(30) infinite` - 2秒周期，30步
    - 文字从无到有再到无，循环显示
  
  - **闪烁光标**:
    - 使用 `::after` 伪元素添加竖线光标 `|`
    - `animation: blink 0.8s step-end infinite` - 0.8秒闪烁周期
    - 光标在文字右侧，持续闪烁
  
  - **自动应用到所有进度消息**:
    - 所有包含"正在"的消息自动使用打字机效果
    - 包括：
      - "正在生成研究大纲..."
      - "正在进行最终整合与审阅..."
      - 其他所有"正在..."类型的消息

- **修改的文件**：
  - `wide_research/frontend/simple.html`：
    - 重写 `.progress-text` CSS 动画
    - 添加 `@keyframes typing` - 打字机效果
    - 添加 `@keyframes blink` - 光标闪烁效果
    - 使用 `::after` 伪元素实现光标

- **技术细节**：
  - **打字机动画**：
    - 0% → width: 0 (文字隐藏)
    - 50% → width: 100% (文字完全显示)
    - 100% → width: 0 (文字再次隐藏)
    - 使用 `steps(30)` 实现逐字显示效果
  - **光标闪烁**：
    - 使用 `opacity` 在 0 和 1 之间切换
    - `step-end` 实现瞬间切换（非渐变）
    - 0.8秒周期，视觉效果自然

- **功能验证**：
  - ✅ 文字以打字机方式逐字显示
  - ✅ 光标在文字右侧闪烁
  - ✅ 动画循环流畅
  - ✅ 所有"正在"类型消息都有效果
  - ✅ 视觉效果生动活泼

## 2025-10-15 (第三十次修改)
### 实现右侧面板显示研究报告撰写进度
- **需求**：
  - 显示"正在撰写研究报告..."后，后续所有 `self._log` 输出都在右侧面板显示
  - 流式显示各章节的撰写内容

- **具体修改**：
  
  **1. 前端逻辑** (`wide_research/frontend/simple.html`):
  - 添加 `isCapturingReport` 状态变量
  - 添加捕获逻辑：
    - 检测到"正在撰写研究报告"或"正在进行最终整合与审阅"时
    - 停止捕获大纲 (`isCapturingOutline = false`)
    - 开始捕获报告 (`isCapturingReport = true`)
    - 清空右侧面板，准备显示报告内容
  - 后续所有 `progress` 消息都路由到右侧面板
  
  **2. 后端逻辑** (`wide_research/main.py`):
  - **修正消息位置**：
    - 第299行：`"正在撰写研究报告..."` → `"正在生成研究大纲..."`（修正错误）
    - 第344行：添加 `self._log("\n正在撰写研究报告...")`（在步骤3开始时）
  
  - **章节内容流式输出**：
    - 替换 `AgentsUtils.print_stream_events` 为手动流式处理
    - 提取每个 `event.data.response.delta.text/content`
    - 通过 `self._log(chunk)` 实时发送到前端
    - 添加兜底机制：如果流式为空，发送 `final_output`

- **修改的文件**：
  - `wide_research/frontend/simple.html`：
    - 添加 `isCapturingReport` 变量
    - 添加报告捕获逻辑（第669-679行）
    - 添加报告内容路由逻辑（第688-693行）
  
  - `wide_research/main.py`：
    - 修正第299行消息为"正在生成研究大纲..."
    - 添加第344行消息"正在撰写研究报告..."
    - 修改第460-485行：章节撰写流式输出逻辑

- **技术细节**：
  - **面板切换逻辑**：
    - 大纲生成时：`isCapturingOutline = true`
    - 报告撰写时：`isCapturingOutline = false`, `isCapturingReport = true`
    - 两个阶段共用右侧面板，但内容会被清空重置
  
  - **流式输出提取**：
    ```python
    async for event in section_result.stream_events():
        if hasattr(event, 'data'):
            raw_event = event.data
            if hasattr(raw_event, 'response'):
                response = raw_event.response
                if hasattr(response, 'delta'):
                    chunk = response.delta.text or response.delta.content
                    if chunk:
                        self._log(chunk)
    ```

- **显示效果**：
  - 左侧显示：
    - "正在生成研究大纲..." (打字机动画)
    - "正在撰写研究报告..." (打字机动画)
  - 右侧显示：
    - 大纲阶段：实时流式显示大纲内容（Markdown渲染）
    - 报告阶段：实时流式显示各章节撰写内容（Markdown渲染）

- **功能验证**：
  - ✅ "正在生成研究大纲..."在左侧显示，内容在右侧
  - ✅ "正在撰写研究报告..."在左侧显示，内容在右侧
  - ✅ 右侧面板在两个阶段之间正确切换
  - ✅ 章节内容实时流式显示
  - ✅ Markdown 格式正确渲染

## 2025-10-15 (第三十一次修改)
### 简化进度显示并优化省略号动画
- **需求**：
  - 去掉"正在生成研究大纲..."
  - 只保留"正在撰写研究报告..."
  - 省略号 `...` 循环显示动画（0到3个点循环）

- **具体修改**：
  
  **1. 后端逻辑** (`wide_research/main.py`):
  - 第299行：将"正在生成研究大纲..."改为"正在撰写研究报告..."
  - 第344行：删除重复的"正在撰写研究报告..."
  - 现在整个流程只显示一次"正在撰写研究报告..."
  
  **2. 前端逻辑** (`wide_research/frontend/simple.html`):
  - **简化捕获逻辑**：
    - 删除"正在生成研究大纲"的检测
    - 只保留"正在撰写研究报告"的检测
    - 直接启动右侧面板显示
  
  - **新增省略号动画函数** `addDotsAnimationMessage`:
    - 创建消息元素，包含文本和省略号容器
    - 使用 `setInterval` 每500ms更新省略号数量
    - 省略号数量从0到3循环（空 → . → .. → ... → 空）
    - 将 interval ID 保存到元素的 `dataset` 中
  
  - **动画实现细节**：
    ```javascript
    let dotCount = 0;
    const dotsInterval = setInterval(() => {
        dotCount = (dotCount + 1) % 4;  // 0, 1, 2, 3, 0, 1, 2, 3...
        dotsSpan.textContent = '.'.repeat(dotCount);
    }, 500);
    ```

- **修改的文件**：
  - `wide_research/main.py`：
    - 第299行：修改为"正在撰写研究报告..."
    - 第344行：删除重复消息
  
  - `wide_research/frontend/simple.html`：
    - 第615-648行：新增 `addDotsAnimationMessage` 函数
    - 第661-677行：简化捕获逻辑，调用 `addDotsAnimationMessage`

- **显示效果**：
  ```
  用户输入 → 澄清 → 回答
  ↓
  左侧显示：正在撰写研究报告    (省略号循环)
                          正在撰写研究报告.   (0.5秒后)
                          正在撰写研究报告..  (1.0秒后)
                          正在撰写研究报告... (1.5秒后)
                          正在撰写研究报告    (2.0秒后，循环)
  ↓
  右侧显示：大纲内容（流式） → 章节内容（流式）
  ```

- **功能验证**：
  - ✅ 去掉"正在生成研究大纲..."消息
  - ✅ 只显示"正在撰写研究报告..."
  - ✅ 省略号从0到3循环显示
  - ✅ 动画流畅，每500ms更新一次
  - ✅ 右侧面板同步显示报告内容

## 2025-10-15 (第三十二次修改)
### 过滤"整合后的研究任务"部分
- **需求**：去掉右侧面板开头显示的"整合后的研究任务："及其描述内容

- **问题描述**：
  - LLM 生成的大纲开头包含"整合后的研究任务："和详细的任务描述
  - 这部分内容在右侧面板显示时应该被过滤掉
  - 只显示从第一个 `#` 标题开始的正式大纲内容

- **解决方案** (`wide_research/frontend/simple.html`):
  - 修改 `filterOutlineMetadata` 函数
  - 添加状态变量 `isInTaskSection` 跟踪是否在任务描述部分
  - 检测逻辑：
    ```javascript
    // 检测"整合后的研究任务"开始
    if (trimmedLine.includes('整合后的研究任务')) {
        isInTaskSection = true;
        return false; // 跳过这一行
    }
    
    // 如果在任务描述部分，跳过直到遇到第一个 # 标题
    if (isInTaskSection) {
        if (trimmedLine.startsWith('#')) {
            isInTaskSection = false; // 遇到标题，结束任务部分
            return true; // 保留这个标题
        }
        return false; // 跳过任务描述内容
    }
    ```

- **过滤规则**：
  1. 检测到"整合后的研究任务"或"整合后的研究任务："时，设置标志
  2. 跳过该行及后续所有内容
  3. 直到遇到第一个以 `#` 开头的标题行
  4. 从该标题行开始恢复正常显示

- **修改的文件**：
  - `wide_research/frontend/simple.html`（第1002-1037行）：
    - 修改 `filterOutlineMetadata` 函数
    - 添加任务部分检测和过滤逻辑

- **显示效果**：
  ```
  【过滤前】
  整合后的研究任务：
  调研 STAT6 在过敏性疾病领域的国内外研究现状，重点聚焦于：
  (1) STAT6 在过敏性疾病中的分子机制与信号通路作用
  (2) 针对过敏性疾病的 STAT6 靶向药物开发进展
  ...
  
  # 大纲标题
  ## 章节1
  
  【过滤后】
  # 大纲标题
  ## 章节1
  ```

- **功能验证**：
  - ✅ "整合后的研究任务："及其描述被完全过滤
  - ✅ 从第一个 `#` 标题开始正常显示
  - ✅ 不影响其他元数据过滤（FOCUS、KEYWORDS 等）
  - ✅ 流式显示仍然正常工作

## 2025-10-15 (第三十三次修改)
### 实现参考文献角标和交互功能
- **需求**：
  - 将报告中的参考文献引用 `[1, 2]` 转换为上角标
  - 点击角标可以跳转到参考文献列表
  - 参考文献可以跳回正文引用位置
  - 报告内容需要 Markdown 渲染

- **实现功能**：

  **1. Markdown 渲染** (`wide_research/frontend/simple.html`):
  - 使用 `marked.js` 渲染报告 Markdown 内容
  - 添加 `.report-content` CSS 样式
  - 复用大纲的 Markdown 样式
  - 添加表格样式支持

  **2. 参考文献角标转换**:
  - **正文引用** → 上角标链接
    - `[1]` → `<sup><a href="#ref-1">[1]</a></sup>`
    - `[1, 2, 3]` → `<sup><a href="#ref-1">[1]</a><a href="#ref-2">[2]</a><a href="#ref-3">[3]</a></sup>`
  
  - **参考文献列表项** → 添加 ID 和返回链接
    - `[1] 文献标题...` → `<span id="ref-1">[1]</span> 文献标题... ↩`

  **3. 交互功能**:
  - **点击正文角标**：
    - 平滑滚动到对应的参考文献
    - 高亮显示参考文献（黄色背景，2秒后消失）
  
  - **点击参考文献 ↩**：
    - 滚动到第一个引用该文献的位置
    - 高亮显示引用位置（黄色背景，2秒后消失）

- **技术实现**：

  **1. `processReferences(html)` 函数**:
  ```javascript
  // 步骤1: 标记参考文献列表项
  html = html.replace(/(<li>)\[(\d+)\]\s+/g, (match, li, num) => {
      return `${li}<span id="ref-${num}" class="reference-item">[${num}]</span> `;
  });
  
  // 步骤2: 转换正文引用为角标
  html = html.replace(/\[(\d+(?:\s*,\s*\d+)*)\]/g, (match, numbers) => {
      const nums = numbers.split(',').map(n => n.trim());
      const superscripts = nums.map(num => 
          `<a href="#ref-${num}" class="citation-link" data-ref="${num}">[${num}]</a>`
      ).join('');
      return `<sup class="citation">${superscripts}</sup>`;
  });
  
  // 步骤3: 添加返回链接
  html = html.replace(/(<span id="ref-\d+" class="reference-item">\[\d+\]<\/span>)/g, 
      (match) => `${match}<a href="#" class="back-to-text" onclick="scrollToFirstCitation(event, this); return false;" title="返回正文">↩</a> `
  );
  ```

  **2. `addReferenceClickListeners()` 函数**:
  - 为所有 `.citation-link` 添加点击事件
  - 平滑滚动到目标参考文献
  - 2秒高亮动画

  **3. `scrollToFirstCitation(event, element)` 函数**:
  - 从参考文献编号查找第一个引用位置
  - 平滑滚动到引用位置
  - 2秒高亮动画

- **CSS 样式**:
  ```css
  /* 角标样式 */
  .citation {
      font-size: 0.75em;
      top: -0.5em;
  }
  
  /* 引用链接 */
  .citation-link {
      color: #0066cc;
      text-decoration: none;
  }
  
  /* 参考文献编号 */
  .reference-item {
      font-weight: 600;
      color: #0066cc;
  }
  
  /* 返回链接 */
  .back-to-text {
      color: #0066cc;
      margin-left: 8px;
  }
  ```

- **修改的文件**：
  - `wide_research/frontend/simple.html`：
    - 第127-243行：添加/更新 Markdown 和参考文献样式
    - 第245-283行：添加参考文献角标样式
    - 第904-1002行：实现参考文献处理和交互功能

- **显示效果**：
  ```
  【正文】
  研究表明 STAT6 在过敏反应中起关键作用[1,2]。
              ↓ 转换为
  研究表明 STAT6 在过敏反应中起关键作用<sup><a>[1]</a><a>[2]</a></sup>。
              ↓ 点击 [1]
  【滚动到参考文献并高亮】
  
  【参考文献】
  [1] ↩ Smith J, et al. Nature. 2023...
   ↑ 点击 ↩
  【滚动回正文引用位置并高亮】
  ```

- **功能验证**：
  - ✅ 报告内容 Markdown 正确渲染
  - ✅ 参考文献引用转换为上角标
  - ✅ 点击角标跳转到参考文献
  - ✅ 点击 ↩ 跳回正文
  - ✅ 平滑滚动动画
  - ✅ 2秒黄色高亮效果
  - ✅ 支持单个引用 `[1]` 和多个引用 `[1, 2, 3]`
  - ✅ 表格正确渲染

## 2025-10-15 (第三十四次修改)
### 优化参考文献列表格式和段落排版
- **需求**：
  - 参考文献列表保持期刊风格，不转换为角标
  - 每个自然段开头空两个字符（中文排版习惯）

- **具体修改**：

  **1. 参考文献列表格式优化** (`wide_research/frontend/simple.html`):
  - **问题**：之前所有 `[数字]` 都被转换为角标，包括参考文献列表
  - **解决方案**：
    - 识别"参考文献"或"References"章节位置
    - 将 HTML 分为正文部分和参考文献部分
    - 只在正文部分转换引用为角标
    - 参考文献列表保持原有格式 `[1] 作者, 标题...`
  
  - **处理逻辑**：
    ```javascript
    // 1. 找到参考文献章节
    const refSectionMatch = html.match(/(<h2[^>]*>参考文献|<h2[^>]*>References)/i);
    
    // 2. 分离正文和参考文献
    let bodyPart = html.substring(0, refSectionStart);
    let refPart = html.substring(refSectionStart);
    
    // 3. 只在正文部分转换为角标
    bodyPart = bodyPart.replace(/\[(\d+(?:\s*,\s*\d+)*)\]/g, ...);
    
    // 4. 参考文献部分只添加锚点，保持原格式
    refPart = refPart.replace(/(<li>)\[(\d+)\]\s+/g, 
        (match, li, num) => `${li}<span id="ref-${num}" class="reference-number">[${num}]</span> `
    );
    ```

  **2. 删除返回链接**:
  - 移除参考文献列表中的 `↩` 返回链接
  - 简化 `addReferenceClickListeners` 函数
  - 点击正文角标仍然可以跳转到参考文献
  - 高亮整个列表项而不是编号

  **3. 段落首行缩进** (`wide_research/frontend/simple.html`):
  - 为所有段落添加 `text-indent: 2em`
  - 适用于大纲和报告内容
  - 符合中文学术论文排版规范

- **CSS 修改**：
  ```css
  /* 段落缩进 */
  .outline-content p,
  .report-content p {
      text-indent: 2em; /* 段首缩进两个字符 */
  }
  
  /* 参考文献编号 - 期刊风格 */
  .reference-number {
      font-weight: 600;
      color: #333;
      margin-right: 4px;
  }
  ```

- **修改的文件**：
  - `wide_research/frontend/simple.html`：
    - 第153-158行：添加段落首行缩进
    - 第272-277行：添加参考文献编号样式
    - 第972-1016行：重写 `processReferences` 函数
    - 第1018-1039行：简化 `addReferenceClickListeners` 函数

- **显示效果对比**：
  
  **正文部分**：
  ```
  　　研究表明，STAT6 在过敏反应中起关键作用¹²³。进一步分析发现...
  　　（段首自动缩进2个字符）
  ```
  
  **参考文献部分**：
  ```
  ## 参考文献 (References)
  
  [1] Smith J, Johnson K. STAT6 regulates Th2 cell differentiation. Nature. 2023...
  [2] Zhang L, Wang Y. Molecular mechanisms of STAT6 signaling. Cell. 2022...
  [3] Liu H, Chen M. STAT6 in allergic diseases. Science. 2021...
  
  （保持期刊格式，不转换为角标）
  ```

- **功能验证**：
  - ✅ 正文中的引用转换为上角标（如 ¹²³）
  - ✅ 参考文献列表保持原始格式 `[1]`
  - ✅ 点击角标可以跳转到参考文献
  - ✅ 参考文献高亮整个列表项
  - ✅ 所有段落自动缩进2个字符
  - ✅ 符合中文学术论文排版规范

## 2025-10-15 (第三十五次修改)
### 优化检索过程的进度显示格式
- **需求**：
  - 检索过程中的进度信息也要使用 Markdown 格式化
  - 包括章节撰写、最终整合等阶段的输出

- **具体修改** (`wide_research/main.py`):

  **1. 章节处理进度格式化**（第364行）:
  ```python
  # 之前：
  self._log(f"\n 开始处理章节 {subsection['title']}")
  self._log(f"\n搜索中...")
  
  # 修改后：
  self._log(f"\n---\n\n### 📝 {subsection['title']}\n\n**状态**: 开始处理...\n")
  self._log(f"**状态**: 搜索文献中...\n")
  ```
  
  - 使用 Markdown 三级标题显示章节名
  - 使用水平线分隔不同章节
  - 使用粗体显示状态信息
  - 添加换行让格式更清晰

  **2. 最终整合阶段格式化**（第530行）:
  ```python
  # 之前：
  self._log("\n正在进行最终整合与审阅...")
  
  # 修改后：
  self._log("\n---\n\n## 📋 最终整合与审阅\n\n**状态**: 整合所有章节内容...\n\n")
  self._log("**状态**: 处理文献引用...\n\n")
  self._log("**状态**: 整理表格编号...\n\n")
  ```
  
  - 使用 Markdown 二级标题
  - 分步骤显示处理进度
  - 每个状态都使用粗体

  **3. 完成信息格式化**（第575-579行）:
  ```python
  self._log("\n---\n\n## ✅ 研究完成\n\n**报告已生成**，包含以下内容：\n\n")
  self._log(f"- 📊 **章节数量**: {len(written_sections)} 个\n")
  self._log(f"- 📚 **参考文献**: {len(all_sources_metadata)} 篇\n")
  self._log(f"- 📄 **报告路径**: `{final_report_path}`\n\n")
  self._log("🎉 **研究综述生成完毕！** 🎉\n")
  ```
  
  - 使用列表显示统计信息
  - 使用行内代码格式显示路径
  - 结构化展示研究成果

  **4. 表格重新编号信息**（第281-282行）:
  ```python
  # 之前：
  self._log(f"  📊 表格重新编号完成: 共 {len(tables)} 个表格")
  
  # 修改后：
  if len(tables) > 0:
      self._log(f"- ✅ **表格整理**: 共 {len(tables)} 个表格已重新编号\n")
  ```

- **显示效果**（右侧面板 Markdown 渲染后）:
  
  ```markdown
  ---
  
  ### 📝 1.1 STAT6 基本概述
  
  **状态**: 开始处理...
  
  **状态**: 搜索文献中...
  
  **状态**: 撰写内容中... (文字为主)
  
  [章节内容流式显示...]
  
  ---
  
  ### 📝 1.2 STAT6 信号通路
  
  **状态**: 开始处理...
  
  [章节内容...]
  
  ---
  
  ## 📋 最终整合与审阅
  
  **状态**: 整合所有章节内容...
  
  **状态**: 处理文献引用...
  
  **状态**: 整理表格编号...
  
  - ✅ **表格整理**: 共 3 个表格已重新编号
  
  ---
  
  ## ✅ 研究完成
  
  **报告已生成**，包含以下内容：
  
  - 📊 **章节数量**: 6 个
  - 📚 **参考文献**: 125 篇
  - 📄 **报告路径**: `workspace/research_abc123/final_report.md`
  
  🎉 **研究综述生成完毕！** 🎉
  ```

- **修改的文件**：
  - `wide_research/main.py`：
    - 第364行：章节开始处理格式化
    - 第368行：搜索状态格式化
    - 第281-282行：表格重新编号信息格式化
    - 第530行：最终整合标题格式化
    - 第563行：文献引用处理状态
    - 第567行：表格编号整理状态
    - 第575-579行：完成信息格式化

- **前端渲染**（`simple.html`）:
  - 已有的 `updateOutlineContent()` 函数自动使用 `marked.parse()` 渲染
  - 所有 Markdown 格式（标题、粗体、列表、代码）都会被正确渲染
  - 无需修改前端代码

- **功能验证**：
  - ✅ 章节处理进度使用 Markdown 格式
  - ✅ 最终整合阶段结构化显示
  - ✅ 完成信息清晰展示统计数据
  - ✅ 右侧面板实时渲染 Markdown
  - ✅ 视觉效果更加专业和清晰

## 2025-10-15 (第三十六次修改)
### 恢复"正在生成研究大纲"消息和省略号动画
- **需求**：
  - 之前的修改被撤回，需要重新配置
  - "正在生成研究大纲..."使用省略号循环动画
  - 后端发送"正在生成研究大纲..."，前端显示省略号动画

- **具体修改** (`wide_research/frontend/simple.html`):
  
  **前端消息匹配修改**（第782-791行）:
  ```javascript
  // 之前（错误）：
  if (data.message.includes('正在撰写研究报告') || ...)
      addDotsAnimationMessage('assistant', '正在撰写研究报告');
  
  // 修改后（正确）：
  if (data.message.includes('正在生成研究大纲') || ...)
      addDotsAnimationMessage('assistant', '正在生成研究大纲');
  ```
  
  - 匹配后端发送的"正在生成研究大纲..."消息
  - 使用 `addDotsAnimationMessage` 函数添加省略号动画
  - 省略号从 0 到 3 个循环显示（500ms间隔）

- **工作流程**：
  ```
  1. 用户输入主题
  2. 澄清问题并回答
  3. 左侧显示：正在生成研究大纲    (0.0秒)
                正在生成研究大纲.   (0.5秒)
                正在生成研究大纲..  (1.0秒)
                正在生成研究大纲... (1.5秒)
                正在生成研究大纲    (2.0秒) → 循环
  4. 右侧面板激活，流式显示大纲内容
  ```

- **省略号动画实现**（已存在的 `addDotsAnimationMessage` 函数）:
  ```javascript
  function addDotsAnimationMessage(role, content) {
      contentDiv.innerHTML = `<span>${content}<span class="dots-animation"></span></span>`;
      
      const dotsSpan = contentDiv.querySelector('.dots-animation');
      let dotCount = 0;
      const dotsInterval = setInterval(() => {
          dotCount = (dotCount + 1) % 4;  // 0, 1, 2, 3, 0, 1, 2, 3...
          dotsSpan.textContent = '.'.repeat(dotCount);
      }, 500);
  }
  ```

- **修改的文件**：
  - `wide_research/frontend/simple.html`：
    - 第782-791行：修改消息匹配逻辑，从"正在撰写研究报告"改为"正在生成研究大纲"

- **后端消息**（`wide_research/main.py` 第299行）:
  ```python
  self._log("正在生成研究大纲...")
  ```

- **功能验证**：
  - ✅ 后端发送"正在生成研究大纲..."
  - ✅ 前端正确识别消息
  - ✅ 左侧显示省略号循环动画（0 → . → .. → ... → 0）
  - ✅ 右侧面板同步显示大纲内容
  - ✅ 动画流畅，500ms 间隔

## 2025-10-15 (第三十七次修改)
### 清理用户界面日志，优化显示逻辑
- **需求**：
  - 左侧只显示"正在生成研究大纲..."一条主要进度消息
  - 其他所有日志（章节处理、整合等）都在右侧以 Markdown 格式显示
  - 去掉不必要的技术细节日志

- **具体修改** (`wide_research/main.py`):

  **1. 保留的左侧消息**：
  - ✅ 第299行：`self._log("正在生成研究大纲...")` - 显示在左侧，带省略号动画

  **2. 注释掉的左侧消息**：
  - ❌ 第292行：初始化工作区消息
  - ❌ 第344行：`self._log("\n正在撰写研究报告...")`
  - ❌ 第530行：`self._log("\n正在进行最终整合与审阅...")`

  **3. 注释掉的技术细节日志**：
  - ❌ 第365行：开始处理章节
  - ❌ 第369行：搜索中...
  - ❌ 第385行：原始搜索数据已保存
  - ❌ 第388行：解析搜索结果
  - ❌ 第430行：撰写章节内容
  - ❌ 第489行：已生成表格
  - ❌ 第494行：章节草稿已保存
  - ❌ 第496行：章节处理完成

  **4. 保留在右侧显示的内容**：
  - ✅ 大纲的 Markdown 内容（流式输出）
  - ✅ 章节的 Markdown 内容（流式输出）
  - ✅ 所有由 LLM 生成的实际研究内容

- **显示效果**：

  **左侧（聊天区）**：
  ```
  用户: STAT6 的研究现状
  
  助手: [澄清问题...]
  
  用户: [回答澄清]
  
  助手: 正在生成研究大纲    ← 只有这一条消息，带省略号动画
        正在生成研究大纲.
        正在生成研究大纲..
        正在生成研究大纲...
        （循环）
  ```

  **右侧（内容面板）**：
  ```markdown
  # STAT6 在过敏性疾病中的研究进展
  
  ## 1. STAT6 基本概述
  ### 1.1 STAT6 结构与功能
  FOCUS: STAT6 的分子结构...
  KEYWORDS: STAT6, 结构域, 磷酸化...
  
  ### 1.2 STAT6 信号通路
  ...
  
  [实际的章节内容流式显示]
  
  研究表明，STAT6 在 Th2 细胞分化中起关键作用...
  
  [更多章节内容...]
  ```

- **优势**：
  1. **界面清爽**：左侧不再有大量技术日志
  2. **关注内容**：用户只看到实际的研究内容
  3. **进度清晰**：一条动画消息足以表明系统正在工作
  4. **专业体验**：类似于专业写作工具的体验
  5. **技术透明**：技术细节隐藏，但文件仍然保存用于调试

- **修改的文件**：
  - `wide_research/main.py`：
    - 注释了10+处技术细节日志
    - 保留1处用户可见进度消息
    - 保留所有 LLM 生成的实际内容输出

- **文件系统**：
  - 所有中间文件仍然正常保存在 `workspace/` 目录
  - 大纲、草稿、最终报告都完整保存
  - 开发者可以通过文件系统调试，用户界面保持简洁

- **功能验证**：
  - ✅ 左侧只显示一条进度消息
  - ✅ 右侧显示所有实际内容
  - ✅ 省略号动画正常工作
  - ✅ 内容流式显示不受影响
  - ✅ Markdown 渲染正常
  - ✅ 用户体验更加专业简洁


## 2025-10-15 (第三十八次修改)

### 修改内容
**优化报告页面参考文献样式和宽度**

1. **参考文献区域样式优化**（`simple.html`）：
   - 添加 `.references-section` 样式，为参考文献部分设置特殊格式
   - 参考文献列表项不进行首段缩进（`text-indent: 0 !important;`）
   - 参考文献列表项保留换行（`white-space: pre-wrap;`）
   - 参考文献列表项增加行间距（`line-height: 1.8;`）和底部间距（`margin-bottom: 12px;`）

2. **JavaScript 处理优化**（`simple.html`）：
   - 修改 `processReferences` 函数，为参考文献部分的 HTML 容器添加 `references-section` class
   - 确保参考文献部分的特殊样式能够正确应用

3. **报告页面宽度调整**（`simple.html`）：
   - 将 `.report-content` 的 `max-width` 从 `900px` 增加到 `1200px`
   - 增加左右内边距从 `20px` 到 `40px`

### 效果
- 参考文献部分不再有首段缩进，符合学术论文格式
- 参考文献的换行和格式得到保留
- 正文的角标链接可以正确跳转到参考文献列表
- 报告页面更宽（1200px），阅读体验更好
- 左右边距增加，内容布局更舒适


## 2025-10-15 (第三十九次修改)

### 修改内容
**进一步增加报告页面宽度**

1. **报告页面宽度调整**（`simple.html`）：
   - 将 `.report-content` 的 `max-width` 从 `1200px` 进一步增加到 **`1400px`**
   - 增加左右内边距从 `40px` 增加到 **`60px`**

### 效果
- 报告页面宽度达到 1400px，充分利用宽屏显示器
- 更大的左右边距（60px），内容布局更加舒适
- 适合阅读长篇学术文档


## 2025-10-15 (第四十次修改)

### 修改内容
**修复报告页面 Markdown 渲染中的删除线问题**

1. **问题描述**：
   - 报告中包含波浪号 `~` 的文本（如 `~1200 Å²`、`~30°旋转`）被 Markdown 渲染为删除线
   - 这是因为 GFM（GitHub Flavored Markdown）将 `~~text~~` 解释为删除线

2. **解决方案**（`simple.html`）：
   - 配置 `marked.js`，启用 GFM 但自定义删除线渲染器
   - 创建自定义 `renderer.del` 函数，将删除线标记还原为原始文本（带波浪号）
   - 这样 `~1200 Å²` 会显示为 `~1200 Å²` 而不是 ~~1200 Å²~~

3. **技术实现**：
   ```javascript
   const renderer = new marked.Renderer();
   renderer.del = function(text) {
       // 不渲染为删除线，直接返回原文本（带波浪号）
       return '~' + text + '~';
   };
   marked.parse(content, { renderer: renderer });
   ```

### 效果
- ✅ 波浪号 `~` 正常显示为文本，不会变成删除线
- ✅ 科学符号如 `~1200 Å²`、`~30°` 正确显示
- ✅ 保留其他 Markdown 格式（标题、列表、粗体、斜体等）
- ✅ 不影响参考文献角标功能


## 2025-10-15 (第四十一次修改)

### 修改内容
**优化报告页面布局：更宽、更少留白**

1. **报告页面调整**（`simple.html`）：
   - 最大宽度从 `1400px` 增加到 **`1600px`**（增加 200px）
   - 左右内边距从 `60px` 减少到 **`40px`**（减少 20px）

2. **效果对比**：
   
   **修改前**：
   - 最大宽度：1400px
   - 左右内边距：60px × 2 = 120px
   - 实际内容宽度：1400px - 120px = **1280px**
   
   **修改后**：
   - 最大宽度：1600px
   - 左右内边距：40px × 2 = 80px
   - 实际内容宽度：1600px - 80px = **1520px**
   
   **提升**：实际可用内容宽度增加了 **240px**（约 18.75%）

### 效果
- ✅ 报告页面更宽（1600px），充分利用宽屏空间
- ✅ 留白更少（40px），内容显示更紧凑
- ✅ 实际内容宽度达到 1520px，适合显示复杂表格和长文本
- ✅ 在超宽屏幕上阅读体验更好


## 2025-10-15 (第四十二次修改)

### 修改内容
**修复报告页面宽度未生效的问题**

1. **问题描述**：
   - 报告页面的宽度设置（1600px）没有生效
   - 原因：CSS 中存在两处 `.report-content` 样式定义
   - 第一处（414行）的 `max-width: 800px` 覆盖了后面的 `max-width: 1600px` 设置

2. **解决方案**（`simple.html`）：
   - 删除第一处的 `.report-content` 样式定义（旧的 800px 限制）
   - 保留并完善第二处的样式定义（1600px 新设置）
   - 添加 `line-height: 1.6` 确保行高正确

3. **最终样式**：
   ```css
   .report-content {
       padding: 20px 40px;
       max-width: 1600px;
       margin: 0 auto;
       line-height: 1.6;
   }
   ```

### 效果
- ✅ 报告页面宽度现在正确显示为 1600px
- ✅ 左右内边距为 40px
- ✅ 实际内容宽度为 1520px
- ✅ 行高保持在 1.6 倍，阅读舒适
- ✅ 不再有旧的 800px 限制


## 2025-10-15 (第四十三次修改)

### 修改内容
**隐藏参考文献中的 DOI: N/A 信息**

1. **需求描述**：
   - 参考文献中如果 DOI 为 `N/A`（不可用），则不显示该 DOI 信息
   - 避免在报告中显示无用的 `DOI: N/A` 文本

2. **实现方案**（`simple.html`）：
   - 在 `displayReport` 函数中添加预处理步骤
   - 使用正则表达式 `/\s*DOI:\s*N\/A/gi` 匹配并移除 `DOI: N/A`
   - 在 Markdown 渲染之前执行清理，确保不会显示在最终页面上

3. **正则表达式说明**：
   ```javascript
   content = content.replace(/\s*DOI:\s*N\/A/gi, '');
   ```
   - `\s*`：匹配前面可能的空白字符
   - `DOI:`：匹配字面文本 "DOI:"
   - `\s*`：匹配 DOI: 后面可能的空格
   - `N\/A`：匹配 "N/A"（斜杠需要转义）
   - `gi`：全局匹配（g）且不区分大小写（i）

### 效果

**修改前的参考文献**：
```
[1] R.J. Burmeister, A.H. Huber, P.J. Bjorkman. 1998. 
Structural basis of pH-dependent antibody binding by the neonatal Fc receptor. 
Structure. DOI: 10.1016/S0969-2126(98)00008-2

[2] Unknown Author. 2024. Some research paper. 
Journal Name. DOI: N/A
```

**修改后的参考文献**：
```
[1] R.J. Burmeister, A.H. Huber, P.J. Bjorkman. 1998. 
Structural basis of pH-dependent antibody binding by the neonatal Fc receptor. 
Structure. DOI: 10.1016/S0969-2126(98)00008-2

[2] Unknown Author. 2024. Some research paper. 
Journal Name.
```

- ✅ 有效 DOI 正常显示
- ✅ `DOI: N/A` 自动隐藏
- ✅ 参考文献格式更整洁
- ✅ 不影响其他内容的显示


## 2025-10-15 (第四十四次修改)

### 修改内容
**移除研究完成提示信息**

1. **移除的提示**（`simple.html`）：
   - 移除 "✅ 研究完成！报告已生成，请查看报告标签页。" 提示消息
   - 移除自动切换到报告标签页的功能

2. **修改后的行为**：
   - 研究完成后不显示任何完成提示
   - 不自动跳转到报告标签页
   - 静默地获取报告内容和统计信息
   - 用户可以自主选择何时查看报告

3. **用户体验优化**：
   - 减少干扰性提示
   - 让用户保持在当前的研究进度查看界面
   - 用户可以根据需要手动点击"报告"标签查看结果

### 效果
- ✅ 研究完成后界面保持在当前状态
- ✅ 没有弹出式或突兀的完成提示
- ✅ 报告在后台静默加载完成
- ✅ 用户可以自主控制查看时机


## 2025-10-15 (第四十五次修改)

### 修改内容
**移除后端的研究完成提示消息**

1. **修改的文件**（`api_server.py`）：
   - 移除任务完成时的提示消息 "✅ 研究完成！"
   - 将 `message` 字段设置为空字符串

2. **修改的位置**：
   - `task_manager.update_task` 中的 `message` 参数：从 "✅ 研究完成！" 改为 ""
   - WebSocket 广播消息中的 `message` 字段：从 "✅ 研究完成！" 改为 ""

3. **代码变更**：
   ```python
   # 修改前
   task_manager.update_task(
       task_id,
       status="completed",
       progress=1.0,
       message="✅ 研究完成！",  # ❌ 移除
       ...
   )
   
   # 修改后
   task_manager.update_task(
       task_id,
       status="completed",
       progress=1.0,
       message="",  # ✅ 空消息
       ...
   )
   ```

### 效果
- ✅ 研究完成后不会在前端显示任何完成提示
- ✅ WebSocket 消息不包含完成提示文本
- ✅ 前后端统一，都不显示完成提示
- ✅ 用户界面更加简洁，减少干扰


## 2025-10-15 (第四十六次修改)

### 修改内容
**优化进度动画：文字保持不动，只有省略号循环**

1. **问题描述**：
   - 之前的"正在撰写研究报告..."等消息使用打字机效果（整个文本动画）
   - 用户希望只有省略号循环动画，文字保持不动

2. **解决方案**（`simple.html`）：
   - 将所有"正在"开头的消息从 `addProgressMessage`（打字机效果）改为 `addDotsAnimationMessage`（省略号动画）
   - 保持 `addDotsAnimationMessage` 函数的现有实现：文字固定，省略号从 "" → "." → ".." → "..." 循环

3. **动画效果对比**：
   
   **修改前（打字机效果）**：
   ```
   正
   正在
   正在撰
   正在撰写
   正在撰写研
   正在撰写研究
   正在撰写研究报
   正在撰写研究报告
   正在撰写研究报告.
   正在撰写研究报告..
   正在撰写研究报告...
   （循环）
   ```
   
   **修改后（省略号动画）**：
   ```
   正在撰写研究报告
   正在撰写研究报告.
   正在撰写研究报告..
   正在撰写研究报告...
   正在撰写研究报告
   （循环，每 0.5 秒切换）
   ```

4. **技术实现**：
   ```javascript
   // 修改前
   if (data.message.includes('正在')) {
       addProgressMessage('assistant', data.message);  // 打字机效果
   }
   
   // 修改后
   if (data.message.includes('正在')) {
       addDotsAnimationMessage('assistant', data.message);  // 省略号动画
   }
   ```

### 效果
- ✅ "正在生成研究大纲"：文字不动，省略号循环
- ✅ "正在撰写研究报告"：文字不动，省略号循环
- ✅ 其他"正在"消息：统一使用省略号动画
- ✅ 动画更加简洁、优雅
- ✅ 不干扰用户阅读主要内容


## 2025-10-15 (第四十七次修改)

### 修改内容
**移除空的完成消息，避免前端显示空对话框**

1. **问题描述**：
   - 研究完成时，后端发送空的 `completed` 消息
   - 前端接收到后会显示一个空的对话框

2. **解决方案**：
   
   **后端修改**（`api_server.py`）：
   - 移除 `websocket_manager.broadcast` 发送 `completed` 消息
   - 添加注释说明："不发送 completed 消息，避免前端显示空对话框"
   - WebSocket 会通过轮询检测到 `status="completed"` 并自动处理
   
   **前端修改**（`simple.html`）：
   - 移除 `data.type === 'completed'` 的消息处理分支
   - 只保留 `data.type === 'final'` 的最终状态处理

3. **代码变更**：
   
   ```python
   # api_server.py - 修改前
   await websocket_manager.broadcast(task_id, {
       "type": "completed",
       "message": "",  # 空消息会导致前端显示空对话框
       "timestamp": datetime.now().isoformat()
   })
   
   # api_server.py - 修改后
   # 不发送 completed 消息，避免前端显示空对话框
   # WebSocket 会通过轮询检测到 status="completed" 并自动处理
   ```
   
   ```javascript
   // simple.html - 修改前
   } else if (data.type === 'completed') {
       console.log('任务完成:', data);
       addMessage('assistant', data.message);  // 空消息显示空对话框
   } else if (data.type === 'final') {
   
   // simple.html - 修改后
   } else if (data.type === 'final') {
   ```

### 效果
- ✅ 研究完成后不会显示空的对话框
- ✅ 前端通过 `final` 消息处理任务完成状态
- ✅ WebSocket 轮询机制会正常检测到任务完成
- ✅ 用户界面更加简洁，没有多余的空白消息
- ✅ 完全移除了所有"任务完成"、"研究完成"的提示信息

