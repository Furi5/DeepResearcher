#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wide Research API Server - FastAPI Backend
基于 main.py 的 FastAPI 后端服务
"""

import asyncio
import json
import pathlib
import traceback
import uuid
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from main import DeepResearchAgent


# === 数据模型 ===
class ResearchRequest(BaseModel):
    """研究请求"""
    query: str
    task_id: Optional[str] = None


class TaskStatus(BaseModel):
    """任务状态"""
    task_id: str
    status: str  # pending, running, completed, failed
    progress: float  # 0.0 - 1.0
    message: str
    created_at: str
    updated_at: str
    result: Optional[str] = None
    statistics: Optional[Dict[str, Any]] = None
    report_path: Optional[str] = None


# === WebSocket 连接管理器 ===
class WebSocketManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, task_id: str, websocket: WebSocket):
        """添加新的 WebSocket 连接"""
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)
    
    def disconnect(self, task_id: str, websocket: WebSocket):
        """移除 WebSocket 连接"""
        if task_id in self.active_connections:
            if websocket in self.active_connections[task_id]:
                self.active_connections[task_id].remove(websocket)
    
    async def broadcast(self, task_id: str, message: dict):
        """向所有连接广播消息"""
        if task_id in self.active_connections:
            for connection in self.active_connections[task_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"广播消息失败: {e}")


# === 任务管理器 ===
class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self.tasks: Dict[str, TaskStatus] = {}
        self.agents: Dict[str, DeepResearchAgent] = {}
        self.clarification_queues: Dict[str, asyncio.Queue] = {}  # 澄清答案队列
        
    def create_task(self, query: str) -> str:
        """创建新任务"""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        now = datetime.now().isoformat()
        
        self.tasks[task_id] = TaskStatus(
            task_id=task_id,
            status="pending",
            progress=0.0,
            message=f"任务已创建: {query}",
            created_at=now,
            updated_at=now
        )
        
        return task_id
    
    def update_task(self, task_id: str, **kwargs):
        """更新任务状态"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            for key, value in kwargs.items():
                setattr(task, key, value)
            task.updated_at = datetime.now().isoformat()
    
    def get_task(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    async def initialize_agent(self, task_id: str) -> DeepResearchAgent:
        """初始化研究 Agent"""
        if task_id not in self.agents:
            agent = DeepResearchAgent()
            await agent.build()
            self.agents[task_id] = agent
        return self.agents[task_id]
    
    def cleanup_agent(self, task_id: str):
        """清理 Agent"""
        if task_id in self.agents:
            del self.agents[task_id]
    
    def create_clarification_queue(self, task_id: str) -> asyncio.Queue:
        """创建澄清答案队列"""
        queue = asyncio.Queue()
        self.clarification_queues[task_id] = queue
        return queue
    
    async def provide_clarification(self, task_id: str, answer: str):
        """提供澄清答案"""
        if task_id in self.clarification_queues:
            await self.clarification_queues[task_id].put(answer)


# === 澄清请求模型 ===
class ClarificationRequest(BaseModel):
    """澄清答案请求"""
    answer: str


# === 全局变量 ===
task_manager = TaskManager()
websocket_manager = WebSocketManager()


# === FastAPI 应用 ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("🚀 Wide Research API Server 启动")
    yield
    print("👋 Wide Research API Server 关闭")


app = FastAPI(
    title="Wide Research API",
    description="深度研究助手 API 服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === API 路由 ===

# 根路径路由已移动到静态文件服务部分


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_tasks": len(task_manager.tasks)
    }


@app.post("/api/research")
async def create_research_task(request: ResearchRequest):
    """
    创建研究任务
    
    Args:
        request: 研究请求
        
    Returns:
        任务 ID 和状态
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="研究主题不能为空")
    
    # 创建任务
    task_id = task_manager.create_task(request.query)
    
    # 后台执行研究
    asyncio.create_task(execute_research_task(task_id, request.query))
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "任务已创建，正在执行中",
        "websocket_url": f"/ws/{task_id}"
    }


@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    """
    获取任务状态
    
    Args:
        task_id: 任务 ID
        
    Returns:
        任务状态
    """
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task


@app.get("/api/download/{task_id}")
async def download_report(task_id: str):
    """
    下载研究报告
    
    Args:
        task_id: 任务 ID
        
    Returns:
        报告文件
    """
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")
    
    if not task.report_path or not pathlib.Path(task.report_path).exists():
        raise HTTPException(status_code=404, detail="报告文件不存在")
    
    return FileResponse(
        path=task.report_path,
        filename=f"research_report_{task_id}.md",
        media_type="text/markdown"
    )


@app.post("/api/clarification/{task_id}")
async def submit_clarification(task_id: str, request: ClarificationRequest):
    """
    提交澄清答案
    
    Args:
        task_id: 任务 ID
        request: 澄清答案
        
    Returns:
        提交状态
    """
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.status != "clarifying":
        raise HTTPException(status_code=400, detail="任务不在澄清状态")
    
    # 提供澄清答案
    await task_manager.provide_clarification(task_id, request.answer)
    
    # 更新任务状态
    task_manager.update_task(task_id, status="researching", message="继续研究...")
    
    return {"status": "success", "message": "澄清答案已提交"}


@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket 连接，实时推送任务进度
    
    Args:
        websocket: WebSocket 连接
        task_id: 任务 ID
    """
    await websocket.accept()
    await websocket_manager.connect(task_id, websocket)
    
    try:
        # 持续发送任务状态更新
        while True:
            task = task_manager.get_task(task_id)
            if not task:
                await websocket.send_json({
                    "type": "error",
                    "message": "任务不存在"
                })
                break
            
            # 发送状态更新
            await websocket.send_json({
                "type": "status",
                "task_id": task.task_id,
                "status": task.status,
                "progress": task.progress,
                "message": task.message,
                "updated_at": task.updated_at
            })
            
            # 如果任务完成或失败，发送最终结果
            if task.status in ["completed", "failed"]:
                await websocket.send_json({
                    "type": "final",
                    "task_id": task.task_id,
                    "status": task.status,
                    "result": task.result,
                    "statistics": task.statistics,
                    "report_path": task.report_path
                })
                break
            
            # 等待后再发送下一次更新
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        print(f"WebSocket 连接断开: {task_id}")
        websocket_manager.disconnect(task_id, websocket)
    except Exception as e:
        print(f"WebSocket 错误: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })


# === 后台任务执行 ===

async def execute_research_task(task_id: str, query: str):
    """
    执行研究任务（后台）
    
    Args:
        task_id: 任务 ID
        query: 研究主题
    """
    # 创建回调函数
    async def progress_callback(data: dict):
        """进度回调函数"""
        message = data.get("message", "")
        task_manager.update_task(task_id, message=message)
        
        # 通过 WebSocket 广播进度
        await websocket_manager.broadcast(task_id, {
            "type": "progress",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    async def clarification_callback(data: dict):
        """澄清回调函数"""
        questions = data.get("questions", "")
        task_manager.update_task(task_id, status="clarifying", message=questions)
        
        # 通过 WebSocket 广播澄清问题
        await websocket_manager.broadcast(task_id, {
            "type": "clarification_needed",
            "questions": questions,
            "timestamp": datetime.now().isoformat()
        })
    
    try:
        def __init__(self, task_id):
            self.task_id = task_id
            self.buffer = io.StringIO()
            self.last_update = time.time()
            
        def write(self, text):
            self.buffer.write(text)
            # 每0.2秒更新一次进度，更频繁的更新
            if time.time() - self.last_update > 0.2:
                self.update_progress()
                self.last_update = time.time()
                
        def update_progress(self):
            content = self.buffer.getvalue()
            if content.strip():
                # 解析进度信息
                progress = self.parse_progress(content)
                print(f"🔄 更新进度: {progress['message']} ({progress['value']*100:.1f}%)")
                task_manager.update_task(
                    self.task_id,
                    progress=progress['value'],
                    message=progress['message']
                )
                
        def parse_progress(self, content):
            """解析输出内容，提取进度信息"""
            lines = content.split('\n')
            last_line = lines[-1].strip() if lines else ""
            
            # 根据输出内容判断进度 - Web 环境不能跳过澄清
            if "步骤 1" in content and "澄清" in content:
                return {"value": 0.1, "message": "🔍 步骤 1: 正在分析并澄清您的调研需求..."}
            elif "步骤 2" in content and "大纲" in content:
                return {"value": 0.2, "message": "📋 步骤 2: 正在生成研究大纲..."}
            elif "步骤 3" in content and "搜索" in content:
                return {"value": 0.3, "message": "🔍 步骤 3: 正在执行深度搜索..."}
            elif "步骤 4" in content and "撰写" in content:
                return {"value": 0.7, "message": "✍️ 步骤 4: 正在撰写综述报告..."}
            elif "研究完成" in content or "✅" in content:
                return {"value": 1.0, "message": "✅ 研究完成！"}
            elif "Web 环境自动跳过澄清" in content:
                return {"value": 0.15, "message": "⏭️ Web 环境自动跳过澄清，使用原始任务。"}
            elif "正在生成研究大纲" in content:
                return {"value": 0.25, "message": "📋 步骤 2: 正在生成研究大纲..."}
            elif "PlannerAgent" in content:
                return {"value": 0.3, "message": "📋 步骤 2: 正在规划研究结构..."}
            elif "SearcherAgent" in content:
                return {"value": 0.4, "message": "🔍 步骤 3: 正在搜索相关文献..."}
            elif "WriterAgent" in content:
                return {"value": 0.7, "message": "✍️ 步骤 4: 正在撰写综述报告..."}
            elif "初始化研究 Agent" in content:
                return {"value": 0.1, "message": "🚀 初始化研究 Agent..."}
            elif "开始深度研究" in content:
                return {"value": 0.2, "message": "🔍 开始深度研究..."}
            else:
                # 显示最后一行输出作为进度信息
                display_text = last_line[:100] if last_line else "🔄 处理中..."
                return {"value": 0.5, "message": f"🔄 {display_text}"}
                
        def flush(self):
            pass
    
    try:
        # 更新状态：初始化
        task_manager.update_task(
            task_id,
            status="running",
            progress=0.1,
            message="🚀 初始化研究 Agent..."
        )
        
        # 初始化 Agent
        agent = await task_manager.initialize_agent(task_id)
        
        # 创建进度捕获器
        progress_capture = ProgressCapture(task_id)
        
        # 更新状态：开始研究
        task_manager.update_task(
            task_id,
            progress=0.2,
            message="🔍 开始深度研究..."
        )
        
        # 执行研究并捕获输出
        with redirect_stdout(progress_capture), redirect_stderr(progress_capture):
            result = await agent.run_streamed(query)
        
        # 查找生成的报告文件
        report_path = pathlib.Path(__file__).parent / "final_report.md"
        
        # 格式化统计信息
        statistics = format_statistics(agent.statistics)
        
        # 更新状态：完成
        task_manager.update_task(
            task_id,
            status="completed",
            progress=1.0,
            message="✅ 研究完成！",
            result=result,
            statistics=statistics,
            report_path=str(report_path) if report_path.exists() else None
        )
        
    except Exception as e:
        error_msg = f"❌ 执行失败：{str(e)}\n\n{traceback.format_exc()}"
        task_manager.update_task(
            task_id,
            status="failed",
            progress=0.0,
            message=error_msg,
            result=error_msg
        )
    finally:
        # 清理 Agent（可选）
        # task_manager.cleanup_agent(task_id)
        pass


def format_statistics(stats: dict) -> dict:
    """格式化统计信息"""
    if not stats:
        return {}
    
    # Token 消耗
    token_usage = stats.get('token_usage', {})
    total_tokens = sum(token_usage.values())
    
    # 检索次数
    search_counts = stats.get('search_counts', {})
    total_searches = sum(search_counts.values())
    
    # 成本估算
    cost_usd = total_tokens * 0.00003
    cost_cny = cost_usd * 7
    
    return {
        "token_usage": token_usage,
        "total_tokens": total_tokens,
        "search_counts": search_counts,
        "total_searches": total_searches,
        "cost": {
            "usd": round(cost_usd, 2),
            "cny": round(cost_cny, 2)
        }
    }


# === 静态文件服务 ===
# 添加根路径，直接返回 simple.html 内容
@app.get("/", include_in_schema=False)
async def root():
    """返回前端页面"""
    from fastapi.responses import FileResponse
    return FileResponse("frontend/simple.html")

# 挂载前端静态文件（放在最后，避免覆盖 API 路由）
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")


def main():
    """主函数"""
    import uvicorn
    
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║                                                        ║
    ║     🔬 Wide Research API Server                       ║
    ║                                                        ║
    ║     📡 API: http://localhost:8000                     ║
    ║     📚 Docs: http://localhost:8000/docs               ║
    ║     🔌 WebSocket: ws://localhost:8000/ws/{task_id}    ║
    ║                                                        ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )


if __name__ == "__main__":
    main()


