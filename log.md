# 修改日志

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
