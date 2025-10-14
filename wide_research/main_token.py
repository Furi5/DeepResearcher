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

from agents import function_tool

from utu.agents import SimpleAgent
from utu.config import ConfigLoader
from utu.tools import SearchToolkit
from utu.tools import SerperToolkit
from utu.utils import AgentsUtils, FileUtils, schema_to_basemodel
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
    
    # Use a regex to find FOCUS and KEYWORDS lines
    focus_regex = re.compile(r"^\s*FOCUS:\s*(.*)", re.IGNORECASE)
    keywords_regex = re.compile(r"^\s*KEYWORDS:\s*(.*)", re.IGNORECASE)

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
                "keywords": []
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
            
    return outline


class DeepResearchAgent:
    def __init__(self):
        # 统计信息
        self.stats = {
            'total_tokens': 0,
            'total_searches': 0,
            'clarifier_tokens': 0,
            'planner_tokens': 0,
            'searcher_tokens': 0,
            'writer_tokens': 0,
            'search_counts': {
                'google_search': 0,
                'scholar_search': 0,
                'news_search': 0,
                'web_qa': 0,
                'image_search': 0,
            }
        }
    
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
        print("🔍 步骤 1: 正在分析并澄清您的调研需求...")
        async with self.clarifier_agent as clarifier:
            clarification_result = await clarifier.run(task)
            run_result = clarification_result.get_run_result()
            clarification_questions = run_result.final_output
            
            # 统计 token - 从 raw_responses 中获取
            if hasattr(run_result, 'raw_responses') and run_result.raw_responses:
                for resp in run_result.raw_responses:
                    if hasattr(resp, 'usage') and resp.usage:
                        tokens = resp.usage.total_tokens
                        self.stats['clarifier_tokens'] += tokens
                        self.stats['total_tokens'] += tokens
                print(f"  💰 步骤1消耗 tokens: {self.stats['clarifier_tokens']}")

        if "无需澄清" not in clarification_questions:
            print(f"\n【澄清问题】:\n{clarification_questions}")
            user_clarifications = input("\n> 请您回答上述问题以获得更精准的报告 (或直接按回车跳过): ")
            if user_clarifications.strip():
                # 这是一个示例 prompt，您可能需要根据实际情况调整
                merge_prompt = PROMPTS["clarifier_merge"].format(task=task, clarification_questions=clarification_questions, user_clarifications=user_clarifications)
                # 假设有一个简单的Agent或LLM调用来完成整合
                # 为简化，这里我们直接拼接
                enhanced_task = merge_prompt
                print("\n✅ 感谢您的澄清！已更新研究任务。")
            else:
                enhanced_task = task
                print("\n⏩ 已跳过澄清，将按原任务执行。")
        else:
            enhanced_task = task
            print("✅ 任务清晰，无需澄清。")
        
        return enhanced_task

    def print_statistics(self):
        """打印统计信息"""
        print("\n" + "="*80)
        print("📊 运行统计信息 (Statistics)")
        print("="*80)
        
        # Token 统计
        print(f"\n💰 Token 消耗统计:")
        print(f"  - 澄清阶段 (Clarifier):     {self.stats['clarifier_tokens']:>10,} tokens")
        print(f"  - 规划阶段 (Planner):       {self.stats['planner_tokens']:>10,} tokens")
        print(f"  - 搜索阶段 (Searcher):      {self.stats['searcher_tokens']:>10,} tokens")
        print(f"  - 写作阶段 (Writer):        {self.stats['writer_tokens']:>10,} tokens")
        print(f"  {'─'*60}")
        print(f"  - 总计 (Total):             {self.stats['total_tokens']:>10,} tokens")
        
        # 检索统计
        print(f"\n🔍 检索次数统计:")
        
        # 显示所有被调用的工具（包括动态添加的）
        tool_display_names = {
            'google_search': 'Google 搜索',
            'scholar_search': '学术搜索',
            'news_search': '新闻搜索',
            'web_qa': '网页内容获取',
            'image_search': '图像搜索',
            'search': '搜索',
            'video_search': '视频搜索',
            'map_search': '地图搜索',
            'place_search': '地点搜索',
            'autocomplete': '自动补全',
            'google_lens': 'Google Lens',
        }
        
        # 按调用次数排序显示
        sorted_tools = sorted(self.stats['search_counts'].items(), key=lambda x: x[1], reverse=True)
        for tool_name, count in sorted_tools:
            display_name = tool_display_names.get(tool_name, tool_name)
            if count > 0:  # 只显示实际被调用的工具
                print(f"  - {display_name:24} {count:>10} 次")
        
        print(f"  {'─'*60}")
        print(f"  - 总计检索次数:             {self.stats['total_searches']:>10} 次")
        
        # 成本估算（假设使用 GPT-4）
        # GPT-4 价格: $0.03/1K input tokens, $0.06/1K output tokens
        # 简化计算，假设输入输出各占一半
        estimated_cost = (self.stats['total_tokens'] / 1000) * 0.045  # 平均值
        print(f"\n💵 估算成本 (基于 GPT-4 价格):")
        print(f"  - 约 ${estimated_cost:.2f} USD")
        print(f"  - 约 ¥{estimated_cost * 7:.2f} CNY (按 1:7 汇率)")
        
        print("="*80 + "\n")
    
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

    async def run_streamed(self, task: str):
        """
        Orchestrates the entire research and writing process from planning to final report.
        """
        # === 步骤 0: 初始化工作区 ===
        project_id = f"research_{uuid.uuid4().hex[:8]}"
        workspace_dir = pathlib.Path(__file__).parent / "workspace" / project_id
        workspace_dir.mkdir(parents=True, exist_ok=True)
        print(f"🚀 初始化成功！为本次研究创建专属工作区: {workspace_dir}")

        try:
            # === 步骤 1: 任务澄清 ===
            enhanced_task = await self._clarify_task(task)

            # === 步骤 2: 生成研究大纲 ===
            print("\n📋 步骤 2: 正在生成研究大纲...")
            async with self.planner_agent as planner:
                plan_result = planner.run_streamed(enhanced_task)
                await AgentsUtils.print_stream_events(plan_result.stream_events())
                markdown_outline = plan_result.final_output
                
                # 统计 token - 从 raw_responses 中获取
                if hasattr(plan_result, 'raw_responses') and plan_result.raw_responses:
                    for resp in plan_result.raw_responses:
                        if hasattr(resp, 'usage') and resp.usage:
                            tokens = resp.usage.total_tokens
                            self.stats['planner_tokens'] += tokens
                            self.stats['total_tokens'] += tokens
                    print(f"  💰 步骤2消耗 tokens: {self.stats['planner_tokens']}")
            
            # 持久化大纲
            outline_path = workspace_dir / "outline.md"
            outline_path.write_text(markdown_outline, encoding='utf-8')
            print(f"  💾 大纲已保存到: {outline_path}")

            parsed_outline = parse_markdown_outline(markdown_outline)
            
            # 持久化解析后的大纲JSON，便于调试
            parsed_outline_path = workspace_dir / "outline.json"
            with parsed_outline_path.open('w', encoding='utf-8') as f:
                json.dump(parsed_outline, f, indent=2, ensure_ascii=False)
            print(f"  ✅ 大纲规划与解析完成！共规划了 {len(parsed_outline.get('sections', []))} 个章节。")

            # === 步骤 3: 迭代式研究与撰写（并行处理） ===
            written_sections = []
            all_sources_metadata = {}

            # 收集所有子章节
            all_subsections = []
            for section in parsed_outline.get("sections", []):
                for subsection in section.get("subsections", []):
                    subsection['sections_title'] = section['title']
                    subsection['sections_id'] = section['id']
                    
                    all_subsections.append(subsection)
            
            print(f"\n📊 准备并行处理 {len(all_subsections)} 个章节...")
            
            # 定义单个子章节的处理函数
            async def process_subsection(subsection, semaphore):
                async with semaphore:
                    sub_id = subsection['id'].replace('.', '_')
                    print(f"\n{'='*25} 开始处理章节 {subsection['id']}: {subsection['title']} {'='*25}")
                    
                    try:
                        # --- 3a. 执行深度搜索 ---
                        print(f"  🔍 [{subsection['id']}] (3a) 搜索中...")
                        searcher_prompt = f"""
                        ### **研究焦点 (Research Focus)**:
                        {subsection['research_focus']}
                        
                        ### **关键词 (Keywords)**:
                        {", ".join(subsection['keywords'])}
                        """
                        
                        # 为每个任务创建独立的 agent 实例
                        async with self.searcher_agent as searcher:
                            result_stream = await searcher.run(searcher_prompt)
                            run_result = result_stream.get_run_result()
                            markdown_data = run_result.final_output
                            
                            # 统计 token - 从 raw_responses 中获取
                            chapter_tokens = 0
                            if hasattr(run_result, 'raw_responses') and run_result.raw_responses:
                                for resp in run_result.raw_responses:
                                    if hasattr(resp, 'usage') and resp.usage:
                                        tokens = resp.usage.total_tokens
                                        chapter_tokens += tokens
                                        self.stats['searcher_tokens'] += tokens
                                        self.stats['total_tokens'] += tokens
                                print(f"  💰 [{subsection['id']}] 搜索消耗 tokens: {chapter_tokens}")
                            
                            # 统计工具调用次数 - 从 new_items 中获取
                            if hasattr(run_result, 'new_items'):
                                from agents import ToolCallItem
                                for item in run_result.new_items:
                                    if isinstance(item, ToolCallItem):
                                        tool_name = item.raw_item.name if hasattr(item.raw_item, 'name') else str(item)
                                        # 调试：打印工具名称
                                        print(f"    🔧 检测到工具调用: {tool_name}")
                                        if tool_name in self.stats['search_counts']:
                                            self.stats['search_counts'][tool_name] += 1
                                            self.stats['total_searches'] += 1
                                        else:
                                            # 工具名称不在预定义列表中，需要动态添加
                                            print(f"    ⚠️ 未知工具类型: {tool_name}")
                                            if tool_name not in self.stats['search_counts']:
                                                self.stats['search_counts'][tool_name] = 0
                                            self.stats['search_counts'][tool_name] += 1
                                            self.stats['total_searches'] += 1
                        
                        (workspace_dir / "data").mkdir(exist_ok=True)
                        search_data_path = workspace_dir / "data" / f"{sub_id}_raw_data.md"
                        search_data_path.write_text(markdown_data, encoding='utf-8')
                        print(f"    💾 [{subsection['id']}] 原始搜索数据已保存: {search_data_path}")
                        
                        # --- 3b. 解析搜索结果 ---
                        print(f"  🧩 [{subsection['id']}] (3b) 解析搜索结果...")
                        
                        raw_posts = [p.strip() for p in re.split(r'----', markdown_data) if p.strip()]
                        context_for_writer = ""
                        
                        if not raw_posts:
                            print(f"    ⚠️ [{subsection['id']}] 警告: 未找到任何文献。将为此章节生成占位内容。")
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
                            post_str = post_str.replace('----', '')
                            post = parse_document(post_str)
                            print('post:',post)
                            print('-'*100)
                            try:
                                post = parse_document(post_str)
                                if (ck := post.get('citation_key')):
                                    all_sources_metadata[ck] = post
                                    context_for_writer += f"### 文献来源: {ck}\n**标题**: {post.get('title', 'N/A')}\n\n{post.get('content', 'N/A')}\n\n"
                                    count += 1
                            except Exception:
                                print(f"    - [{subsection['id']}] 解析某篇文献失败，已跳过。")
                        
                        print(f"    ✅ [{subsection['id']}] 解析完成，处理了 {count} 篇文献。")
                        
                        # --- 3c. 撰写章节内容 ---
                        print(f"  ✍️  [{subsection['id']}] (3c) 撰写章节内容...")
                        writer_prompt = PROMPTS["section_writer"].format(
                            subsection_title=subsection['title'],
                            subsection_focus=subsection['research_focus'],
                            context_for_writer=context_for_writer
                        )
                        
                        # 为每个任务创建独立的 writer 实例
                        writer = SimpleAgent(
                            name=f"SectionWriterAgent_{sub_id}",
                            instructions=PROMPTS["section_writer"],
                        )
                        
                        async with writer:
                            section_result = writer.run_streamed(writer_prompt)
                            await AgentsUtils.print_stream_events(section_result.stream_events())
                            written_content = section_result.final_output
                            
                            # 统计 writer token - 从 raw_responses 中获取
                            chapter_writer_tokens = 0
                            if hasattr(section_result, 'raw_responses') and section_result.raw_responses:
                                for resp in section_result.raw_responses:
                                    if hasattr(resp, 'usage') and resp.usage:
                                        tokens = resp.usage.total_tokens
                                        chapter_writer_tokens += tokens
                                        self.stats['writer_tokens'] += tokens
                                        self.stats['total_tokens'] += tokens
                                print(f"  💰 [{subsection['id']}] 写作消耗 tokens: {chapter_writer_tokens}")
                        
                        (workspace_dir / "drafts").mkdir(exist_ok=True)
                        draft_path = workspace_dir / "drafts" / f"{sub_id}_draft.md"
                        draft_path.write_text(written_content, encoding='utf-8')
                        print(f"    💾 [{subsection['id']}] 章节草稿已保存: {draft_path}")
                        
                        print(f"✅ [{subsection['id']}] 章节处理完成！")
                        return {
                            'sections_id': subsection['sections_id'],
                            'sections_title': subsection['sections_title'],
                            "id": subsection['id'], 
                            "title": subsection['title'], 
                            "content": written_content,
                            "order": subsection['id']
                        }
                    
                    except Exception as e:
                        print(f"❌ [{subsection['id']}] 处理出错: {e}")
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
            print(f"\n{"="*25} 步骤 4: 正在进行最终整合与审阅 {'='*25}")

            # 准备最终 prompt 所需的材料
            title = parsed_outline.get("title", "未命名综述")
            full_content = f"# {title}\n\n"
            current_section_id = None # 用于追踪当前的章节ID

            for section in written_sections:
                # 检查是否进入了一个新的大章节
                if section['sections_id'] != current_section_id:
                    full_content += f"# {section['sections_title']}\n\n"
                    current_section_id = section['sections_id'] # 更新当前章节ID

                # 根据是否为第一章，决定如何添加内容
                if current_section_id == '1':
                    # 第一章：不添加小标题
                    full_content += f"{section['content']}\n\n"
                else:
                    # 其他章节：添加小标题
                    full_content += f"### {section['title']}\n{section['content']}\n\n"
        
            all_sources_metadata_json = json.dumps(all_sources_metadata, indent=2, ensure_ascii=False)
            
            # 持久化整合前的材料
            (workspace_dir / "final_inputs").mkdir(exist_ok=True)
            (workspace_dir / "final_inputs" / "full_content.md").write_text(full_content, encoding='utf-8')
            (workspace_dir / "final_inputs" / "all_metadata.json").write_text(all_sources_metadata_json, encoding='utf-8')

            
            final_output = self.process_draft(full_content, all_sources_metadata)

            
            # 持久化最终报告
            final_report_path = workspace_dir / "final_report.md"
            final_report_path.write_text(final_output, encoding='utf-8')
            print(f"  💾 最终报告已保存: {final_report_path}")

            print("\n🎉🎉🎉 研究综述生成完毕！ 🎉🎉🎉")
            
            # 打印统计信息
            self.print_statistics()
            
            # 保存统计信息到文件
            stats_path = workspace_dir / "statistics.json"
            with stats_path.open('w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
            print(f"📊 统计信息已保存到: {stats_path}")
            
            return final_output

        except Exception as e:
            print(f"\n❌ 在执行过程中发生严重错误: {e}")
            traceback.print_exc()
            # 即使出错也显示已收集的统计信息
            self.print_statistics()
            return f"任务执行失败。请检查工作区文件夹 '{workspace_dir}' 中的日志和中间文件以进行调试。"


async def main():
    deep_research = DeepResearchAgent()
    await deep_research.build()
    query = input("What would you like to research? ")
    query = query.strip() or TASK
    print(f"Processing task: {query}")
    result = await deep_research.run_streamed(query)

    with open("final_report.md", "w") as f:
        f.write(result)
    print(f"{'-' * 80}\n{result}\n{'-' * 80}")


if __name__ == "__main__":
    asyncio.run(main())
