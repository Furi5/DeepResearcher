# pylint: disable=line-too-long
# ruff: noqa: E501
"""
https://manus.im/blog/introducing-wide-research
"""

import asyncio
import json
import pathlib
import traceback
import re
import uuid
import yaml
import httpx
import httpcore

from agents import function_tool

from utu.agents import SimpleAgent
from utu.config import ConfigLoader
from utu.tools import SearchToolkit, SerperToolkit
from utu.utils import AgentsUtils, FileUtils
from utu.utils.Citation import CitationProcessor

PROMPTS = FileUtils.load_yaml(pathlib.Path(__file__).parent / "prompts.yaml")
SEARCH_TOOLKIT = SearchToolkit(ConfigLoader.load_toolkit_config("search"))
SERPER_TOOLKIT = SerperToolkit(ConfigLoader.load_toolkit_config("serper"))
CONCURRENCY = 20


def parse_document(text):
    """
    解析 YAML 格式的文档
    
    Args:
        text: YAML 格式的文本
        
    Returns:
        dict: 解析后的字典，包含所有字段
    """
    try:
        # 直接用 yaml.safe_load 解析
        data = yaml.safe_load(text)
        return data if data else {}
    except yaml.YAMLError as e:
        print(f"YAML 解析错误: {e}")
        return {}

def parse_markdown_outline(markdown_text: str) -> dict:
    """
    Parses a structured Markdown outline into a nested dictionary.
    """
    lines = markdown_text.strip().split('\n')
    
    outline = {"title": "", "sections": []}
    current_section = None
    
    # Use a regex to find FOCUS, KEYWORDS, TABLE_RECOMMENDED and TABLE_NUMBER lines
    focus_regex = re.compile(r"^\s*FOCUS:\s*(.*)", re.IGNORECASE)
    keywords_regex = re.compile(r"^\s*KEYWORDS:\s*(.*)", re.IGNORECASE)
    table_regex = re.compile(r"^\s*TABLE_RECOMMENDED:\s*(.*)", re.IGNORECASE)
    table_number_regex = re.compile(r"^\s*TABLE_NUMBER:\s*(.*)", re.IGNORECASE)
     
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Main Title
        if line.startswith('# '):
            outline["title"] = line[2:].strip()
            continue

        # Section Title
        if line.startswith('## '):
            section_title = line[3:].strip()
            current_section = {
                "title": section_title,
                "id": section_title.split('.')[0],
                "subsections": []
            }
            outline["sections"].append(current_section)
            continue
            
        # Subsection Title
        if line.startswith('### '):
            if current_section is None:
                # Handle case where a subsection appears before a section
                continue
            
            subsection_title = line[4:].strip()
            subsection_data = {
                "title": subsection_title,
                "id": subsection_title.split(' ')[0],
                "research_focus": "",
                "keywords": [],
                "table_recommended": False,  # 默认不建议表格
                "table_number": None  # 默认无表格编号
            }
            current_section["subsections"].append(subsection_data)
            continue
            
        # Focus Line
        focus_match = focus_regex.match(line)
        if focus_match:
            if current_section and current_section["subsections"]:
                current_section["subsections"][-1]["research_focus"] = focus_match.group(1).strip()
            continue

        # Keywords Line
        keywords_match = keywords_regex.match(line)
        if keywords_match:
            if current_section and current_section["subsections"]:
                keywords_str = keywords_match.group(1).strip()
                keywords_list = [k.strip() for k in keywords_str.split(',')]
                current_section["subsections"][-1]["keywords"] = keywords_list
            continue
        
        # Table Recommended Line
        table_match = table_regex.match(line)
        if table_match:
            if current_section and current_section["subsections"]:
                table_value = table_match.group(1).strip().upper()
                current_section["subsections"][-1]["table_recommended"] = (table_value == "YES")
            continue
        
        # Table Number Line
        table_number_match = table_number_regex.match(line)
        if table_number_match:
            if current_section and current_section["subsections"]:
                table_num_str = table_number_match.group(1).strip()
                # 如果是 N/A 或空，则为 None；否则尝试转换为整数
                if table_num_str.upper() != "N/A" and table_num_str:
                    try:
                        current_section["subsections"][-1]["table_number"] = int(table_num_str)
                    except ValueError:
                        current_section["subsections"][-1]["table_number"] = None
            continue
            
    return outline


class DeepResearchAgent:
    def __init__(self, progress_callback=None, clarification_callback=None, chat_callback=None):
        self.table_counter = 0  # 全局表格计数器
        self.progress_callback = progress_callback
        self.clarification_callback = clarification_callback
        self.chat_callback = chat_callback  # 用于发送聊天消息到左侧对话框
        self.clarification_queue = None  # 澄清答案队列
        self.report_path = None  # 最终报告路径
    
    def _log(self, message: str):
        """替代 print，通过回调发送到后端（右侧面板）"""
        if self.progress_callback:
            asyncio.create_task(self.progress_callback({
                "type": "progress",
                "message": message
            }))
        else:
            print(message)  # 降级到普通 print
    
    def _log_chat(self, message: str):
        """发送消息到左侧对话框"""
        if self.chat_callback:
            asyncio.create_task(self.chat_callback({
                "type": "chat",
                "message": message
            }))
        else:
            print(message)  # 降级到普通 print
    
    async def wait_for_clarification(self):
        """等待澄清答案"""
        if self.clarification_queue:
            return await self.clarification_queue.get()
        return ""
    
    def set_clarification_queue(self, queue):
        """设置澄清答案队列"""
        self.clarification_queue = queue
        
    async def build(self):
        # 1. 澄清 Agent
        self.clarifier_agent = SimpleAgent(
            name="ClarifierAgent",
            instructions=PROMPTS["clarifier"],
        )
        
        # 2. 规划 Agent
        self.planner_agent = SimpleAgent(
            name="PlannerAgent",
            instructions=PROMPTS["planner_new"], # 需要一个新的 Prompt，指导它只生成大纲JSON
  
        )
        
        self.searcher_agent = SimpleAgent(
            name="SearcherAgent",
            instructions=PROMPTS["searcher_cn"], # 我们将创建这个新 Prompt
            tools=SEARCH_TOOLKIT.get_tools_in_agents() + SERPER_TOOLKIT.get_tools_in_agents()
        )
        
        # 3. 章节撰写 Agent (原 Formatter，但 Prompt 聚焦于单章节写作)
        self.section_writer_agent = SimpleAgent(
            name="SectionWriterAgent",
            instructions=PROMPTS["section_writer"], # 新 Prompt，指导它根据资料撰写特定章节
        )



    async def _clarify_task(self, task: str) -> str:
        """Helper function to handle the clarification step."""
        async with self.clarifier_agent as clarifier:
            clarification_result = clarifier.run_streamed(task)
            # 澄清阶段的流式输出发送到左侧对话框
            await AgentsUtils.print_stream_events(
                    clarification_result.stream_events(),
                    callback=lambda text: self._log_chat(text) if text.strip() else None
                )
            clarification_questions = clarification_result.final_output

        if "无需澄清" not in clarification_questions:
            # 通过回调通知后端需要澄清
            if self.clarification_callback:
                await self.clarification_callback({
                    "type": "clarification_needed",
                    "questions": clarification_questions
                })
            
            # 等待澄清答案
            user_clarifications = await self.wait_for_clarification()
            
            if user_clarifications.strip():
                # 这是一个示例 prompt，您可能需要根据实际情况调整
                merge_prompt = PROMPTS["clarifier_merge"].format(task=task, clarification_questions=clarification_questions, user_clarifications=user_clarifications)
                # 假设有一个简单的Agent或LLM调用来完成整合
                # 为简化，这里我们直接拼接
                enhanced_task = merge_prompt
            else:
                enhanced_task = task
        else:
            enhanced_task = task
            # self._log("✅ 任务清晰，无需澄清。")
        
        return enhanced_task

    def process_draft(self, draft_content: str, metadata: dict) -> str:
        """
        处理初稿，插入文献引用
        
        Args:
            draft_content: 初稿内容（Markdown 格式）
            metadata: 参考文献元数据字典
            
        Returns:
            处理后的完整文档（包含参考文献列表）
        """
        processor = CitationProcessor(metadata)
        processed_content, reference_list = processor.process(draft_content)
        
        # 组装最终文档
        final_document = f"{processed_content}\n\n## 参考文献 (References)\n\n{reference_list}"
        
        return final_document
    
    def renumber_tables(self, content: str) -> str:
        """
        重新整理表格编号，确保表格编号连续（表1、表2、表3...）
        
        Args:
            content: 包含表格的文档内容
            
        Returns:
            重新编号后的文档内容
        """
        import re
        
        # 找出所有表格标题（格式：**表 X. 标题**）
        table_pattern = r'\*\*表\s+(\d+)\.\s+([^\*]+)\*\*'
        tables = list(re.finditer(table_pattern, content))
        
        if not tables:
            return content  # 没有表格，直接返回
        
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
        
        
        return content

    async def run_streamed(self, task: str):
        """
        Orchestrates the entire research and writing process from planning to final report.
        """
        # === 步骤 0: 初始化工作区 ===
        project_id = f"research_{uuid.uuid4().hex[:8]}"
        workspace_dir = pathlib.Path(__file__).parent / "workspace" / project_id
        workspace_dir.mkdir(parents=True, exist_ok=True)
        # self._log(f"🚀 初始化成功！为本次研究创建专属工作区: {workspace_dir}")

        try:
            # === 步骤 1: 任务澄清 ===
            enhanced_task = await self._clarify_task(task)

            # === 步骤 2: 生成研究大纲 ===
            self._log("正在撰写研究报告")
            async with self.planner_agent as planner:
                plan_result = planner.run_streamed(enhanced_task)
                # 使用 callback 将流式输出发送到前端
                await AgentsUtils.print_stream_events(
                    plan_result.stream_events(),
                    callback=lambda text: self._log(text) if text else None
                )
                # 获取最终输出（如果流式输出没有内容，使用最终输出）
                markdown_outline = plan_result.final_output
            
            # 将完整大纲发送到前端（确保右侧显示完整内容）
            # self._log(f"\n{markdown_outline}\n")
            
            # 持久化大纲
            outline_path = workspace_dir / "outline.md"
            outline_path.write_text(markdown_outline, encoding='utf-8')

            parsed_outline = parse_markdown_outline(markdown_outline)
            
            # 持久化解析后的大纲JSON，便于调试
            parsed_outline_path = workspace_dir / "outline.json"
            with parsed_outline_path.open('w', encoding='utf-8') as f:
                json.dump(parsed_outline, f, indent=2, ensure_ascii=False)

            # === 步骤 3: 迭代式研究与撰写（并行处理） ===
            
            written_sections = []
            all_sources_metadata = {}

            self._log("\n\n# 开始撰写所有子章节\n\n")
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
            
            # 定义单个子章节的处理函数
            async def process_subsection(subsection, semaphore):
                async with semaphore:
                    sub_id = subsection['id'].replace('.', '_')
                    self._log(f"\n开始处理章节 {subsection['title']}")
                    
                    try:
                        # --- 3a. 执行深度搜索 ---
                        self._log(f"\n[{subsection['id']}]搜索中...")
                        searcher_prompt = f"""
                        ### **研究焦点 (Research Focus)**:
                        {subsection['research_focus']}
                        
                        ### **关键词 (Keywords)**:
                        {", ".join(subsection['keywords'])}
                        """
                        
                        async with self.searcher_agent as searcher:
                            # 增加 max_turns 避免复杂搜索时超限
                            result_stream = searcher.run_streamed(searcher_prompt)
                            
                            # 添加重试机制处理网络连接错误
                            max_retries = 3
                            retry_count = 0
                            markdown_data = None
                            
                            while retry_count < max_retries:
                                try:
                                    await AgentsUtils.print_stream_events(result_stream.stream_events())
                                    markdown_data = result_stream.final_output
                                    break
                                except (httpx.RemoteProtocolError, httpcore.RemoteProtocolError) as e:
                                    retry_count += 1
                                    self._log(f"    ⚠️ 网络连接错误 (尝试 {retry_count}/{max_retries}): {str(e)}")
                                    if retry_count < max_retries:
                                        await asyncio.sleep(2 ** retry_count)  # 指数退避
                                        # 重新创建流式连接
                                        result_stream = searcher.run_streamed(searcher_prompt)
                                    else:
                                        self._log(f"    ❌ 网络连接失败，跳过此章节: {subsection['id']}")
                                        markdown_data = f"【网络连接错误】处理此章节时出错: {str(e)}"
                                        break
                                except Exception as e:
                                    self._log(f"    ❌ 其他错误: {str(e)}")
                                    markdown_data = f"【处理错误】处理此章节时出错: {str(e)}"
                                    break
                        
                        (workspace_dir / "data").mkdir(exist_ok=True)
                        search_data_path = workspace_dir / "data" / f"{sub_id}_raw_data.md"
                        search_data_path.write_text(markdown_data, encoding='utf-8')
                        # self._log(f"    💾 [{subsection['id']}] 原始搜索数据已保存: {search_data_path}")
                        
                        # --- 3b. 解析搜索结果 ---
                        # self._log(f"  🧩 [{subsection['id']}] (3b) 解析搜索结果...")
                        
                        raw_posts = [p.strip() for p in re.split(r'----', markdown_data) if p.strip()]
                        context_for_writer = ""
                        
                        if not raw_posts:
                            # self._log(f"    ⚠️ [{subsection['id']}] 警告: 未找到任何文献。将为此章节生成占位内容。")
                            return {
                                'sections_id': subsection['sections_id'],
                                'sections_title': subsection['sections_title'],
                                "id": subsection['id'], 
                                "title": subsection['title'], 
                                "content": "【编者注：未能找到相关参考文献，此章节内容缺失。】",
                                "order": subsection['id']
                            }
                        
                        count = 0
                        for post_str in raw_posts:
                            try:
                                post_str = post_str.replace('----', '')
                                post = parse_document(post_str)
                                
                                # 检查解析结果是否为字典
                                if not isinstance(post, dict):
                                    # self._log(f"[{subsection['id']}] 警告: 解析结果不是字典，跳过")
                                    continue
                                
                                # 检查是否有 citation_key
                                if (ck := post.get('citation_key')):
                                    all_sources_metadata[ck] = post
                                    context_for_writer += f"### 文献来源: {ck}\n**标题**: {post.get('title', 'N/A')}\n\n{post.get('content', 'N/A')}\n\n"
                                    count += 1
                            except Exception as e:
                                # self._log(f"[{subsection['id']}] 解析某篇文献失败: {str(e)}，已跳过。")
                                traceback.print_exc()
                        
                        # self._log(f"[{subsection['id']}] 解析完成，处理了 {count} 篇文献。")
                        
                        # --- 3c. 撰写章节内容 ---
                        # 获取 planner 的表格建议和编号
                        table_recommended = subsection.get('table_recommended', False)
                        planner_table_number = subsection.get('table_number', None)
                        
                        # 使用 planner 建议的编号，如果没有则使用预分配的编号
                        assigned_table_number = planner_table_number if planner_table_number else subsection['assigned_table_number']
                        
                        # table_status = f"✅ 建议表格{assigned_table_number}" if table_recommended else "📝 文字为主"
                        # self._log(f"  ✍️  [{subsection['id']}] (3c) 撰写章节内容... ({table_status})")
                        table_instruction = ""
                        
                        if table_recommended:
                            table_instruction = f"""
---
**📊 表格建议**：Planner 建议本章节使用表格来展示对比或汇总信息。
- **表格编号**：**{assigned_table_number}**
- **重要**：生成表格时，必须在正文段落中引用表格，使用"如表{assigned_table_number}所示"、"详见表{assigned_table_number}"等表述。
- 表格应放在正文末尾，作为内容的总结和补充。
"""
                        else:
                            table_instruction = f"""
---
**📝 写作建议**：本章节主要使用文字论述即可，通常不需要表格。
除非遇到特别适合表格展示的密集数据，否则请用清晰的文字表述内容。
如果确实需要表格，可使用编号：**{assigned_table_number}**，并在正文中引用。
"""
                        
                        writer_prompt = f"""
### **章节标题**: {subsection['title']}

### **章节焦点**: {subsection['research_focus']}

### **相关研究资料**:
{context_for_writer}
{table_instruction}
"""
                        

                        async with self.section_writer_agent as writer:
                            section_result = writer.run_streamed(writer_prompt)
                            await AgentsUtils.print_stream_events(section_result.stream_events())
                            written_content = section_result.final_output
                            
                        
                        # 检查是否包含表格
                        # if f"**表 {assigned_table_number}." in written_content:
                        #     self._log(f"    📊 [{subsection['id']}] 已生成表格：表 {assigned_table_number}")
                        
                        (workspace_dir / "drafts").mkdir(exist_ok=True)
                        draft_path = workspace_dir / "drafts" / f"{sub_id}_draft.md"
                        draft_path.write_text(written_content, encoding='utf-8')
                        # self._log(f"    💾 [{subsection['id']}] 章节草稿已保存: {draft_path}")
                        
                        self._log(f"\n\n[{subsection['id']}] 章节撰写完成！")
                        
                        # 将章节内容发送到前端右侧面板显示
                        # self._log(f"\n### {subsection['title']}\n{written_content}\n")
                        
                        return {
                            'sections_id': subsection['sections_id'],
                            'sections_title': subsection['sections_title'],
                            "id": subsection['id'], 
                            "title": subsection['title'], 
                            "content": written_content,
                            "order": subsection['id']
                        }
                    
                    except Exception as e:
                        # self._log(f"❌ [{subsection['id']}] 处理出错: {e}")
                        traceback.print_exc()
                        return {
                            'sections_id': subsection['sections_id'],
                            'sections_title': subsection['sections_title'],
                            "id": subsection['id'], 
                            "title": subsection['title'], 
                            "content": f"【编者注：处理此章节时出错: {str(e)}】",
                            "order": subsection['id']
                        }
            
            # 使用信号量限制并发数量
            semaphore = asyncio.Semaphore(CONCURRENCY)
            
            # 并行处理所有子章节
            tasks = [process_subsection(subsection, semaphore) for subsection in all_subsections]
            results = await asyncio.gather(*tasks)
            
            # 按照原始顺序排序结果
            written_sections = sorted(results, key=lambda x: x['order'])
            

            # === 步骤 4: 最终整合与审阅 ===
            # self._log("\n正在进行最终整合与审阅...")

            # 准备最终 prompt 所需的材料
            title = parsed_outline.get("title", "未命名综述")
            full_content = f"# {title}\n\n"
            
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
        
            all_sources_metadata_json = json.dumps(all_sources_metadata, indent=2, ensure_ascii=False)
            
            # 持久化整合前的材料
            (workspace_dir / "final_inputs").mkdir(exist_ok=True)
            (workspace_dir / "final_inputs" / "full_content.md").write_text(full_content, encoding='utf-8')
            (workspace_dir / "final_inputs" / "all_metadata.json").write_text(all_sources_metadata_json, encoding='utf-8')

            # 处理文献引用
            final_output = self.process_draft(full_content, all_sources_metadata)
            
            # 重新整理表格编号，确保连续性
            final_output = self.renumber_tables(final_output)
            
            # 持久化最终报告
            final_report_path = workspace_dir / "final_report.md"
            final_report_path.write_text(final_output, encoding='utf-8')
            # self._log(f"  💾 最终报告已保存: {final_report_path}")
            
            # 保存报告路径到实例属性，供 API 服务器使用
            self.report_path = str(final_report_path.absolute())

            # 发送报告完成通知，包含完整的报告内容
            if self.progress_callback:
                print(f"[DEBUG] 准备发送 report_completed，final_output 长度: {len(final_output) if final_output else 0}")
                print(f"[DEBUG] final_output 预览: {final_output[:200] if final_output else 'None'}...")
                await self.progress_callback({
                    "type": "report_completed",
                    "message": "综述撰写完成！",
                    "report_content": final_output
                })
            
            return final_output

        except Exception as e:
            # self._log(f"\n❌ 在执行过程中发生严重错误: {e}")
            traceback.print_exc()
            return f"任务执行失败。请检查工作区文件夹 '{workspace_dir}' 中的日志和中间文件以进行调试。"


async def main():
    deep_research = DeepResearchAgent()
    await deep_research.build()
    
    # 检查是否在 Web 环境中运行
    import sys
    if hasattr(sys, 'ps1') or sys.stdin.isatty():
        # 交互式环境，可以正常使用 input()
        query = input("What would you like to research? ")
        if not query.strip():
            print("❌ 错误: 请输入研究主题")
            return
    else:
        # Web 环境，使用默认查询或从环境变量获取
        query = "STAT6 在特应性皮炎中的研究进展"  # 默认查询
        print(f"Web 环境使用默认查询: {query}")
    
    print(f"Processing task: {query}")
    result = await deep_research.run_streamed(query)

    with open("final_report.md", "w") as f:
        f.write(result)
    print(f"{'-' * 80}\n{result}\n{'-' * 80}")


if __name__ == "__main__":
    asyncio.run(main())
