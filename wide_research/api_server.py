#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wide Research API Server - FastAPI Backend
基于 main.py 的 FastAPI 后端服务，支持澄清功能
"""

import asyncio
import json
import pathlib
import traceback
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

from main import DeepResearchAgent


# === 数据模型 ===
class ResearchRequest(BaseModel):
    """研究请求"""
    query: str
    task_id: Optional[str] = None


class ClarificationRequest(BaseModel):
    """澄清答案请求"""
    answer: str


class TaskStatus(BaseModel):
    """任务状态"""
    task_id: str
    status: str  # pending, clarifying, researching, completed, failed
    progress: float  # 0.0 - 1.0
    message: str
    created_at: str
    updated_at: str
    result: Optional[str] = None
    statistics: Optional[Dict[str, Any]] = None
    report_path: Optional[str] = None
    clarification_questions: Optional[str] = None  # 澄清问题


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
        self.clarification_queues: Dict[str, asyncio.Queue] = {}
        
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
    
    def create_clarification_queue(self, task_id: str) -> asyncio.Queue:
        """创建澄清答案队列"""
        queue = asyncio.Queue()
        self.clarification_queues[task_id] = queue
        return queue
    
    async def provide_clarification(self, task_id: str, answer: str):
        """提供澄清答案"""
        if task_id in self.clarification_queues:
            await self.clarification_queues[task_id].put(answer)


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
    """创建研究任务"""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="研究主题不能为空")
    
    task_id = task_manager.create_task(request.query)
    asyncio.create_task(execute_research_task(task_id, request.query))
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "任务已创建，正在执行中",
        "websocket_url": f"/ws/{task_id}"
    }


@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@app.post("/api/clarification/{task_id}")
async def submit_clarification(task_id: str, request: ClarificationRequest):
    """提交澄清答案"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.status != "clarifying":
        raise HTTPException(status_code=400, detail="任务不在澄清状态")
    
    await task_manager.provide_clarification(task_id, request.answer)
    task_manager.update_task(task_id, status="researching", message="继续研究...")
    
    return {"status": "success", "message": "澄清答案已提交"}


@app.post("/api/new-task/{task_id}")
async def create_new_task(task_id: str, request: ResearchRequest):
    """为现有任务创建新的研究"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="研究主题不能为空")
    
    # 重置任务状态
    task_manager.update_task(
        task_id,
        status="pending",
        progress=0.0,
        message=f"新任务已创建: {request.query}",
        result=None,
        statistics=None,
        report_path=None,
        clarification_questions=None
    )
    
    # 启动新任务
    asyncio.create_task(execute_research_task(task_id, request.query))
    
    return {
        "status": "success", 
        "message": "新任务已创建，正在执行中",
        "task_id": task_id
    }


@app.get("/api/download/{task_id}")
async def download_report(task_id: str):
    """下载研究报告"""
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


@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket 连接，实时推送任务进度"""
    await websocket.accept()
    await websocket_manager.connect(task_id, websocket)
    
    try:
        while True:
            task = task_manager.get_task(task_id)
            if not task:
                await websocket.send_json({
                    "type": "error",
                    "message": "任务不存在"
                })
                break
            
            await websocket.send_json({
                "type": "status",
                "task_id": task.task_id,
                "status": task.status,
                "progress": task.progress,
                "message": task.message,
                "updated_at": task.updated_at
            })
            
            if task.status in ["completed", "failed"]:
                # 等待一小段时间，确保所有消息都已广播
                await asyncio.sleep(0.5)
                
                await websocket.send_json({
                    "type": "final",
                    "task_id": task.task_id,
                    "status": task.status,
                    "result": task.result,
                    "statistics": task.statistics,
                    "report_path": task.report_path
                })
                
                # 再等待一小段时间，确保前端接收到消息
                await asyncio.sleep(2.0)  # 增加等待时间
                
                # 不关闭 WebSocket，保持连接以便继续生成新报告
                # 发送任务完成通知，但保持连接开启
                await websocket.send_json({
                    "type": "task_completed",
                    "message": "任务已完成，可以继续生成新报告",
                    "can_continue": True
                })
                
                # 继续轮询，等待新任务
                continue
            
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(task_id, websocket)
    except Exception as e:
        print(f"WebSocket 错误: {e}")
    finally:
        # 确保连接被清理
        websocket_manager.disconnect(task_id, websocket)


# === 后台任务执行 ===

async def execute_research_task(task_id: str, query: str):
    """执行研究任务（后台）"""
    
    # 创建回调函数
    async def progress_callback(data: dict):
        """进度回调函数"""
        message_type = data.get("type", "progress")
        message = data.get("message", "")
        
        # 处理报告完成的特殊情况
        if message_type == "report_completed":
            report_content = data.get("report_content", "")
            print(f"[DEBUG] 发送 report_completed 消息，内容长度: {len(report_content) if report_content else 0}")
            print(f"[DEBUG] 内容预览: {report_content[:200] if report_content else 'None'}...")
            
            task_manager.update_task(task_id, message=message)
            await websocket_manager.broadcast(task_id, {
                "type": "report_completed",
                "message": message,
                "report_content": report_content,
                "timestamp": datetime.now().isoformat()
            })
        else:
            # 普通进度消息
            task_manager.update_task(task_id, message=message)
            await websocket_manager.broadcast(task_id, {
                "type": "progress",
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
    
    async def clarification_callback(data: dict):
        """澄清回调函数"""
        questions = data.get("questions", "")
        task_manager.update_task(
            task_id, 
            status="clarifying",
            message="等待澄清输入...",
            clarification_questions=questions
        )
        await websocket_manager.broadcast(task_id, {
            "type": "clarification_needed",
            "questions": questions,
            "timestamp": datetime.now().isoformat()
        })
    
    async def chat_callback(data: dict):
        """聊天回调函数（发送到左侧对话框）"""
        message = data.get("message", "")
        await websocket_manager.broadcast(task_id, {
            "type": "chat",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    try:
        task_manager.update_task(
            task_id,
            status="running",
            message="🚀 初始化研究 Agent..."
        )
        
        # 创建澄清队列
        clarification_queue = task_manager.create_clarification_queue(task_id)
        
        # 初始化 Agent 并传入回调函数
        agent = DeepResearchAgent(
            progress_callback=progress_callback,
            clarification_callback=clarification_callback,
            chat_callback=chat_callback
        )
        await agent.build()
        agent.set_clarification_queue(clarification_queue)
        
        task_manager.update_task(task_id, message="🔍 开始深度研究...")
        
        # 执行研究
        result = await agent.run_streamed(query)
        
        # 从 agent 实例获取报告路径
        report_path = getattr(agent, 'report_path', None)
        
        # 格式化统计信息
        statistics = format_statistics(getattr(agent, 'statistics', {}))
        
        # 发送报告完成消息，触发前端显示右侧面板
        await websocket_manager.broadcast(task_id, {
            "type": "show_report_panel",
            "message": "报告生成完成，显示右侧面板",
            "timestamp": datetime.now().isoformat()
        })
        
        # 等待确保 report_completed 消息被前端接收和处理
        # 这很重要，因为状态更新为 completed 后 WebSocket 会关闭
        await asyncio.sleep(2.0)  # 增加等待时间，确保前端完全处理报告内容
        
        # 更新状态：完成
        task_manager.update_task(
            task_id,
            status="completed",
            progress=1.0,
            message="",
            result=result,
            statistics=statistics,
            report_path=report_path
        )
        
        # 发送最终完成消息，包含完整的报告内容
        await websocket_manager.broadcast(task_id, {
            "type": "final_completed",
            "message": "综述撰写完成！",
            "result": result,
            "statistics": statistics,
            "report_path": report_path,
            "timestamp": datetime.now().isoformat()
        })
        
        # 再等待一段时间，确保前端接收到最终消息
        await asyncio.sleep(1.0)
        
    except Exception as e:
        error_msg = f"❌ 执行失败：{str(e)}"
        task_manager.update_task(
            task_id,
            status="failed",
            message=error_msg,
            result=error_msg
        )
        
        await websocket_manager.broadcast(task_id, {
            "type": "error",
            "message": error_msg,
            "timestamp": datetime.now().isoformat()
        })


def format_statistics(stats: dict) -> dict:
    """格式化统计信息"""
    if not stats:
        return {}
    
    token_usage = stats.get('token_usage', {})
    total_tokens = sum(token_usage.values())
    search_counts = stats.get('search_counts', {})
    total_searches = sum(search_counts.values())
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
@app.get("/", include_in_schema=False)
async def root():
    """返回前端页面"""
    return FileResponse("frontend/simple.html")

# 静态文件服务，但不覆盖根路径
app.mount("/static", StaticFiles(directory="frontend"), name="static")


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

