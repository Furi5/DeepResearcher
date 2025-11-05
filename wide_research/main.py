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
from utu.tools import SearchToolkit, SerperToolkit, SerpApiToolkit
from utu.utils import AgentsUtils, FileUtils, WebhookManager
from utu.utils.Citation import CitationProcessor
from utu.utils.text_process import parse_document, parse_markdown_outline
from utu.utils.text_process import process_draft, renumber_tables

PROMPTS = FileUtils.load_yaml(pathlib.Path(__file__).parent / "prompts.yaml")
CONCURRENCY = 20



class DeepResearchAgent:
    def __init__(
        self, 
        webhook_url: str | None = None, 
        task_id: str | None = None,
        use_fixed_workspace: bool = False
    ):
        self.table_counter = 0  # 全局表格计数器
        self.clarification_queue = None  # 澄清答案队列
        self.report_path = None  # 最终报告路径
        self.progress_callback = None  # 进度回调函数
        self.use_fixed_workspace = use_fixed_workspace  # 是否使用固定工作区
        
        # 初始化 webhook 管理器
        self.webhook_manager = WebhookManager(webhook_url, task_id)
        
        # 初始化工具（带 webhook）
        self.search_toolkit = SearchToolkit(
            ConfigLoader.load_toolkit_config("search"),
            webhook_manager=self.webhook_manager
        )
        # 使用 SerpApi（支持多搜索引擎）
        self.serpapi_toolkit = SerpApiToolkit(
            ConfigLoader.load_toolkit_config("serpapi"),
            webhook_manager=self.webhook_manager
        )
        # SerperToolkit 暂时禁用（API Key 无效）
        # self.serper_toolkit = SerperToolkit(
        #     ConfigLoader.load_toolkit_config("serper"),
        #     webhook_manager=self.webhook_manager
        # )
        
        # 进度追踪
        self.progress_counter = 0  # 当前完成的步骤数
        self.total_steps = 0  # 总步骤数（子章节数 × 2）
        self.progress_lock = asyncio.Lock()  # 用于线程安全的进度更新
    
    async def build(self):
        # 创建一个简单的callback处理器
        class SimpleCallbackHandler:
            def __init__(self, webhook_manager):
                self.webhook_manager = webhook_manager

            async def send_step_update(self, data):
                """发送步骤更新"""
                if data.get("search_type") == "tool_searching":
                    # 发送工具搜索的详细 callback
                    await self.webhook_manager.send_callback(
                        status="running",
                        results_type="tool_search",
                        step={
                            "name": "ToolSearching",
                            "description": "工具搜索",
                            "message": f"正在分析和查询{data.get('search_query', '')}相关信息..."
                        },
                        data=[{
                            "tool_name": data.get('tool_name', ''),
                            "search_query": data.get('search_query', ''),
                            "found_urls": data.get('found_urls', []),
                            "url_count": data.get('url_count', 0)
                        }]
                    )
                    
                    # 同时发送搜索结果更新（用于白名单过滤）
                    if data.get("found_urls"):
                        await self.webhook_manager.send_search_result(
                            data.get("search_query", ""),
                            [{"url": url, "title": f"Search result {i+1}", "snippet": f"From {data.get('tool_name', 'unknown')}"} 
                             for i, url in enumerate(data.get("found_urls", []))]
                        )

        callback = SimpleCallbackHandler(self.webhook_manager)

        self.planner_agent = SimpleAgent(
            name="PlannerAgent",
            instructions=PROMPTS["planner_new"], # 需要一个新的 Prompt，指导它只生成大纲JSON

        )

        # 创建工具 callback 支持
        async def tool_callback(data):
            """工具回调函数"""
            await callback.send_step_update(data)

        def wrap_tool_with_callback(original_func, callback_func):
            """包装工具函数以添加 callback 支持"""
            async def wrapped_tool(*args, **kwargs):
                # 如果原函数支持 callback 参数，则添加
                import inspect
                sig = inspect.signature(original_func)
                if 'callback' in sig.parameters:
                    kwargs['callback'] = callback_func
                return await original_func(*args, **kwargs)
            
            # 保留原函数的元数据（函数名、文档字符串等）
            wrapped_tool.__name__ = original_func.__name__
            wrapped_tool.__doc__ = original_func.__doc__
            wrapped_tool.__annotations__ = original_func.__annotations__
            
            return wrapped_tool

        # 获取原始工具函数并包装
        search_tools = []
        
        # 处理 SearchToolkit 的工具
        for tool_name, tool_func in self.search_toolkit.get_tools_map_func().items():
            wrapped_func = wrap_tool_with_callback(tool_func, tool_callback)
            search_tools.append(function_tool(wrapped_func, strict_mode=False))
        
        # 处理 SerpApiToolkit 的工具
        for tool_name, tool_func in self.serpapi_toolkit.get_tools_map_func().items():
            wrapped_func = wrap_tool_with_callback(tool_func, tool_callback)
            search_tools.append(function_tool(wrapped_func, strict_mode=False))

        self.searcher_agent = SimpleAgent(
            name="SearcherAgent",
            instructions=PROMPTS["searcher_cn"],
            tools=search_tools
        )
        
        self.section_writer_agent = SimpleAgent(
            name="SectionWriterAgent",
            instructions=PROMPTS["section_writer"], # 新 Prompt，指导它根据资料撰写特定章节
        )

    async def _initialize_workspace(self, task: str) -> pathlib.Path:
        """步骤 0: 初始化工作区"""
        if self.use_fixed_workspace:
            # 使用固定的工作区（用于测试和调试）
            project_id = "test_workspace"
        else:
            # 每次创建新的工作区（用于生产）
            project_id = f"research_{uuid.uuid4().hex[:8]}"
        
        workspace_dir = pathlib.Path(__file__).parent / "workspace" / project_id
        workspace_dir.mkdir(parents=True, exist_ok=True)
        return workspace_dir

    async def _generate_outline(self, task: str) -> dict:
        """步骤 1: 生成研究大纲"""
        async with self.planner_agent as planner:
            plan_result = await planner.run(task)
            markdown_outline = plan_result.get_run_result().final_output

        # 持久化大纲
        outline_path = workspace_dir / "outline.md"
        outline_path.write_text(markdown_outline, encoding='utf-8')

        parsed_outline = parse_markdown_outline(markdown_outline)

        return parsed_outline

    async def _prepare_subsections(self, parsed_outline: dict) -> list:
        """步骤 2: 准备子章节数据"""
        all_subsections = []
        for section in parsed_outline.get("sections", []):
            for subsection in section.get("subsections", []):
                subsection['sections_title'] = section['title']
                subsection['sections_id'] = section['id']

                # 为每个章节预先分配一个潜在的表格编号（避免并行冲突）
                self.table_counter += 1
                subsection['assigned_table_number'] = self.table_counter

                all_subsections.append(subsection)
        
        # 设置总步骤数：每个子章节需要搜索 + 撰写 = 2 步
        self.total_steps = len(all_subsections) * 2
        
        return all_subsections

    async def _process_single_subsection(self, subsection: dict) -> tuple[dict, dict]:
        """处理单个子章节的完整流程，返回 (章节结果, 来源元数据)"""
        sub_id = subsection['id'].replace('.', '_')
        section_id = subsection['id']
        section_title = subsection['title']

        try:
            # --- 3a. 执行深度搜索 ---
            markdown_data = await self._perform_research_search(subsection, sub_id)

            # 搜索完成，更新进度
            async with self.progress_lock:
                self.progress_counter += 1
                percentage = int((self.progress_counter / self.total_steps) * 100) if self.total_steps > 0 else 0
                

            # --- 3b. 解析搜索结果 ---
            context_for_writer, sources_metadata = await self._parse_search_results(
                markdown_data, subsection, sub_id) 

            # --- 3c. 撰写章节内容 ---
            written_content = await self._write_section_content(subsection, context_for_writer, sub_id)

            # 撰写完成，更新进度
            async with self.progress_lock:
                self.progress_counter += 1
                percentage = int((self.progress_counter / self.total_steps) * 100) if self.total_steps > 0 else 0
                
                # print(f"✅ [撰写完成] {section_id} {section_title} - 进度: {self.progress_counter}/{self.total_steps} ({percentage}%)")
                await self.webhook_manager.send_section_completed(
                    section_id, section_title, self.progress_counter, self.total_steps
                )

            section_result = {
                'sections_id': subsection['sections_id'],
                'sections_title': subsection['sections_title'],
                "id": subsection['id'],
                "title": subsection['title'],
                "content": written_content,
                "order": subsection['id']
            }

            return section_result, sources_metadata

        except Exception as e:
            error_msg = str(e)
            # print(f"❌ [错误] {section_id} {section_title} - {error_msg[:100]}")
            traceback.print_exc()
            
            # 如果是 API 错误，发送错误 webhook
            if "402" in error_msg or "Insufficient Balance" in error_msg:
                await self.webhook_manager.send_error(
                    "E5003", 
                    f"章节 {section_id} 处理失败: API 余额不足，请充值"
                )
            elif "503" in error_msg or "502" in error_msg or "API" in error_msg:
                await self.webhook_manager.send_error(
                    "E5002", 
                    f"章节 {section_id} 处理失败: API 服务暂时不可用"
                )
            
            section_result = {
                'sections_id': subsection['sections_id'],
                'sections_title': subsection['sections_title'],
                "id": subsection['id'],
                "title": subsection['title'],
                "content": f"【编者注：处理此章节时出错，请稍后重试】",
                "order": subsection['id']
            }
            return section_result, {}

    async def _perform_research_search(self, subsection: dict, sub_id: str) -> str:
        """执行深度搜索"""
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

                    if retry_count < max_retries:
                        await asyncio.sleep(2 ** retry_count)  # 指数退避
                        # 重新创建流式连接
                        result_stream = searcher.run_streamed(searcher_prompt)
                    else:
                        markdown_data = f"【网络连接错误】处理此章节时出错: {str(e)}"
                        break
                except Exception as e:
                    markdown_data = f"【处理错误】处理此章节时出错: {str(e)}"
                    break

        return markdown_data

    async def _parse_search_results(self, markdown_data: str, subsection: dict, sub_id: str) -> tuple[str, dict]:
        """解析搜索结果"""
        raw_posts = [p.strip() for p in re.split(r'----', markdown_data) if p.strip()]
        context_for_writer = ""
        all_sources_metadata = {}

        if not raw_posts:
            return context_for_writer, all_sources_metadata

        count = 0
        for post_str in raw_posts:
            try:
                post_str = post_str.replace('----', '')
                post = parse_document(post_str)

                # 检查解析结果是否为字典
                if not isinstance(post, dict):
                    continue

                # 检查是否有 citation_key
                if (ck := post.get('citation_key')):
                    all_sources_metadata[ck] = post
                    context_for_writer += f"### 文献来源: {ck}\n**标题**: {post.get('title', 'N/A')}\n\n{post.get('content', 'N/A')}\n\n"
                    count += 1
                    # print(f"[DEBUG] Found citation_key: {ck}")
                else:
                    # print(f"[DEBUG] No citation_key in post: {post.keys() if post else 'None'}")
            except Exception as e:
                traceback.print_exc()

        return context_for_writer, all_sources_metadata

    async def _write_section_content(self, subsection: dict, context_for_writer: str,
                                   sub_id: str) -> str:
        """撰写章节内容"""
        # 获取 planner 的表格建议和编号
        table_recommended = subsection.get('table_recommended', False)
        planner_table_number = subsection.get('table_number', None)

        # 使用 planner 建议的编号，如果没有则使用预分配的编号
        assigned_table_number = planner_table_number if planner_table_number else subsection['assigned_table_number']

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


        return written_content

    async def _process_subsections_parallel(self, all_subsections: list) -> tuple[list, dict]:
        """步骤 3: 并行处理所有子章节"""
        written_sections = []
        all_sources_metadata = {}

        # 定义单个子章节的处理函数
        async def process_subsection(subsection, semaphore):
            async with semaphore:
                section_result, sources_metadata = await self._process_single_subsection(subsection)
                return section_result, sources_metadata

        # 使用信号量限制并发数量
        semaphore = asyncio.Semaphore(CONCURRENCY)

        # 并行处理所有子章节
        tasks = [process_subsection(subsection, semaphore) for subsection in all_subsections]
        results = await asyncio.gather(*tasks)

        # 分离章节结果和元数据，并合并所有元数据
        for section_result, sources_metadata in results:
            written_sections.append(section_result)
            all_sources_metadata.update(sources_metadata)

        # 按照原始顺序排序结果
        written_sections = sorted(written_sections, key=lambda x: x['order'])

        return written_sections, all_sources_metadata

    async def _integrate_final_report(self, parsed_outline: dict, written_sections: list,
                                    all_sources_metadata: dict) -> str:
        """步骤 4: 最终整合与审阅"""
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


        # 处理文献引用
        # print(f"[DEBUG] all_sources_metadata keys: {list(all_sources_metadata.keys()) if all_sources_metadata else 'Empty'}")
        final_output = process_draft(full_content, all_sources_metadata)

        # 重新整理表格编号，确保连续性
        final_output = renumber_tables(final_output)

        # 从 final_output 中解析参考文献列表
        citations = self._parse_citations_from_report(final_output)
        
        await self.webhook_manager.send_final_result(final_output, citations)

        return final_output
    
    def _parse_citations_from_report(self, final_output: str) -> dict:
        """从最终报告中解析参考文献列表
        
        Args:
            final_output: 最终报告内容
            
        Returns:
            dict: {编号: 参考文献内容}，例如 {"1": "[1] Author. Year. Title...", "2": ...}
        """
        citations = {}
        
        # 查找参考文献部分
        ref_section_match = re.search(r'## 参考文献.*?\n\n(.*)', final_output, re.DOTALL)
        if not ref_section_match:
            # print("[WARNING] 未找到参考文献部分")
            return citations
        
        references_text = ref_section_match.group(1)
        
        # 解析每个参考文献条目：[数字] 内容
        pattern = r'\[(\d+)\]\s+(.+?)(?=\n\[|\n\n|\Z)'
        matches = re.findall(pattern, references_text, re.DOTALL)
        
        for num, content in matches:
            # 清理内容（去除多余的换行）
            content = content.strip().replace('\n', ' ')
            citations[num] = f"[{num}] {content}"
        
        # print(f"✅ 解析到 {len(citations)} 条参考文献")
        return citations

    async def run_streamed(self, parsed_outline: dict):
        """
        Orchestrates the entire research and writing process from planning to final report.
        """
        try:
            # print("\n" + "="*80)
            # print("🚀 开始研究任务")
            # print("="*80)
            

            # === 步骤 2: 准备子章节数据 ===
            # print("\n📝 步骤 2: 准备子章节数据...")
            all_subsections = await self._prepare_subsections(parsed_outline)
            # print(f"✅ 准备完成: {len(all_subsections)} 个子章节")
            # print(f"📊 总步骤数: {self.total_steps} (搜索 + 撰写)")
            # print("\n" + "="*80)
            # print("🔍 开始并行处理 (搜索 + 撰写)")
            # print("="*80)

            # === 步骤 3: 迭代式研究与撰写（并行处理） ===
            written_sections, all_sources_metadata = await self._process_subsections_parallel(
                all_subsections)
            
            # print("\n" + "="*80)
            # print("✅ 所有章节处理完成!")
            # print(f"📚 完成章节数: {len(written_sections)}")
            # print(f"📖 收集文献数: {len(all_sources_metadata)}")
            # print("="*80)

            # === 步骤 4: 最终整合与审阅 ===
            # print("\n🔄 步骤 4: 整合最终报告...")
            final_output = await self._integrate_final_report(
                parsed_outline, written_sections, all_sources_metadata)
            
            # print("\n" + "="*80)
            # print("🎉 研究任务完成!")
            # print(f"📄 报告长度: {len(final_output)} 字符")
            # print("="*80)

            # 发送报告完成通知，包含完整的报告内容
            if self.progress_callback:
                # print(f"[DEBUG] 准备发送 report_completed，final_output 长度: {len(final_output) if final_output else 0}")
                # print(f"[DEBUG] final_output 预览: {final_output[:200] if final_output else 'None'}...")
                await self.progress_callback({
                    "type": "report_completed",
                    "message": "综述撰写完成！",
                    "report_content": final_output
                })

            return final_output

        except Exception as e:
            traceback.print_exc()
            error_msg = f"任务执行失败: {str(e)}"
            await self.webhook_manager.send_error("E5001", error_msg)


async def main():
    # 方式1: 使用默认测试配置 + 固定工作区（推荐用于测试）
    deep_research = DeepResearchAgent(use_fixed_workspace=True)
    await deep_research.build()
    
    query = "STAT6在特应性皮炎中的研究进展"
    print(f"🚀 开始研究任务: {query}")
    print(f"🆔 Task ID: {deep_research.webhook_manager.task_id}")
    print(f"💾 Callback 日志: {deep_research.webhook_manager.log_file}")
    print(f"🌐 HTTP 发送: {'启用' if deep_research.webhook_manager.send_http else '禁用（仅保存到文件）'}")
    print("-" * 80)
    
    
    outline_path = "/Users/fl/Desktop/my_code/DeepResearcher/wide_research/outline.json"
            
    with open(outline_path, "r", encoding='utf-8') as f:
        parsed_outline = json.load(f)
        
    result = await deep_research.run_streamed(parsed_outline)
    
    # 保存结果
    with open("final_report.md", "w", encoding='utf-8') as f:
        f.write(result)
    print(f"\n✅ 报告已保存到 final_report.md")
    print(f"{'-' * 80}\n{result[:500]}...\n{'-' * 80}")
    
    # 清理资源并显示回调总结
    await deep_research.webhook_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
