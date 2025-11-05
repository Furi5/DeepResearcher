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
from utu.utils.text_process import parse_document, parse_markdown_outline

PROMPTS = FileUtils.load_yaml(pathlib.Path(__file__).parent / "prompts.yaml")
SEARCH_TOOLKIT = SearchToolkit(ConfigLoader.load_toolkit_config("search"))
SERPER_TOOLKIT = SerperToolkit(ConfigLoader.load_toolkit_config("serper"))
CONCURRENCY = 20



class ClarifyAgent:
    def __init__(self):
        self.clarification_queue = None
        self._clarification_cache = None  # 缓存澄清检查结果

    
    async def wait_for_clarification(self):
        """等待澄清答案"""
        user_clarifications = ""
        while not user_clarifications.strip():
            user_clarifications = input("请输入您的澄清答案: ")
        return user_clarifications
    
    def set_clarification_queue(self, queue):
        """设置澄清答案队列"""
        self.clarification_queue = queue
        
    async def build(self):
        self.clarifier_agent = SimpleAgent(
            name="ClarifierAgent",
            instructions=PROMPTS["clarifier"],
        )
        
        self.merge_agent = SimpleAgent(
            name="merge_agent",
        )
        
    async def run_streamed(self, task: str):
        """运行澄清流程"""
        async with self.clarifier_agent as clarifier:
            clarification_result = await clarifier.run(task)
            clarification_questions = clarification_result.get_run_result().final_output
        
        if "无需澄清" not in clarification_questions:
            print(f"需要澄清问题: {clarification_questions}")
            user_clarifications = await self.wait_for_clarification()
            
            print(f"用户澄清答案: {user_clarifications}")
            async with self.merge_agent as merge:
                result = await merge.run(PROMPTS["clarifier_merge"].format(
                    task=task, 
                    clarification_questions=clarification_questions, 
                    user_clarifications=user_clarifications))
                return result.final_output
        else:
            return task
    
async def main():
    clarify_agent = ClarifyAgent()
    await clarify_agent.build()
    query = "STAT6 在特应性皮炎中的研究进展"
    result = await clarify_agent.run_streamed(query)
    print(f"{'-' * 80}\n{result}\n{'-' * 80}")




if __name__ == "__main__":
    asyncio.run(main())
