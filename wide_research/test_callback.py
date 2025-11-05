"""
简单测试 Webhook Callback 保存功能
不需要 OpenAI API
"""

import asyncio
from utu.utils import WebhookManager

async def main():
    print("=" * 80)
    print("🧪 测试 Callback 保存功能")
    print("=" * 80)
    
    # 初始化 webhook 管理器
    webhook_manager = WebhookManager(
        task_id="callback_test",
        save_to_file=True
    )
    
    print(f"\n📁 Callback 将保存到: {webhook_manager.log_file}")
    print(f"🆔 Task ID: {webhook_manager.task_id}")
    print("-" * 80)
    
    # 1. 发送搜索结果 callback
    print("\n1️⃣ 发送搜索结果回调...")
    await webhook_manager.send_search_result(
        query="STAT6 特应性皮炎",
        whitelist_results=[
            {
                "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
                "title": "STAT6 在特应性皮炎中的作用",
                "snippet": "STAT6 是重要的信号转导因子..."
            },
            {
                "url": "https://www.nature.com/articles/test123",
                "title": "STAT6 信号通路研究",
                "snippet": "研究发现 STAT6 在..."
            }
        ]
    )
    
    # 2. 发送搜索完成 callback
    print("\n2️⃣ 发送搜索完成回调...")
    await webhook_manager.send_search_completed(
        section_id="1.1",
        section_title="STAT6的信号转导机制",
        completed=1,
        total=10
    )
    
    # 3. 发送撰写完成 callback
    print("\n3️⃣ 发送撰写完成回调...")
    await webhook_manager.send_section_completed(
        section_id="1.1",
        section_title="STAT6的信号转导机制",
        completed=2,
        total=10
    )
    
    # 4. 发送更多进度
    print("\n4️⃣ 发送更多进度回调...")
    for i in range(3, 7):
        section_num = (i // 2) + 1
        phase = "search" if i % 2 == 1 else "writing"
        
        if phase == "search":
            await webhook_manager.send_search_completed(
                section_id=f"1.{section_num}",
                section_title=f"测试章节 {section_num}",
                completed=i,
                total=10
            )
        else:
            await webhook_manager.send_section_completed(
                section_id=f"1.{section_num}",
                section_title=f"测试章节 {section_num}",
                completed=i,
                total=10
            )
    
    # 5. 发送最终结果
    print("\n5️⃣ 发送最终结果回调...")
    await webhook_manager.send_final_result(
        report_content="# STAT6 研究综述\n\n这是测试报告...",
        citations=[
            {
                "source": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
                "title": "STAT6 在特应性皮炎中的作用",
                "snippet": "摘要内容..."
            }
        ]
    )
    
    # 清理并显示总结
    await webhook_manager.cleanup()
    
    print("\n" + "=" * 80)
    print("✅ 测试完成！")
    print("=" * 80)
    print(f"\n💡 查看保存的 callback:")
    print(f"   打开文件: {webhook_manager.log_file}")
    print(f"   或使用命令: cat {webhook_manager.log_file}")
    print()

if __name__ == "__main__":
    asyncio.run(main())

