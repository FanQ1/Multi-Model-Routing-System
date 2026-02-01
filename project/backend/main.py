
import uuid
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn

from entity.models import (
    ModelRegistration, ModelInfo, RoutingDecision, RoutingBatch,
    PerformanceReport, ViolationReport, TrustScoreUpdate, CapabilityRanks
)
# from blockchain_service import blockchain
from service.router_service import router
from service.capability_service import capability_service
from service.memory_manager import memory_manager
from entity.database import Conversation, init_db, get_db, Model, RoutingRecord, PerformanceRecord, ViolationRecord
from sqlalchemy.orm import Session
from schema import ApiResponse

app = FastAPI(
    title="ModelChain API",
    description="Blockchain-based trust layer for AI model routing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

    # Initialize capability service and load models
    capability_service._initialize_from_db()


# ============ Model Registry Endpoints ============

@app.post("/api/models/register", response_model=ApiResponse)
async def register_model(
    model_data: ModelRegistration,
    db: Session = Depends(get_db)
):
    """
    注册模型到 数据库（Model）内存和blockchain
    """
    # 1. 注册模型到内存
    try:
        # 计算能力矩阵
        ranks_dict = [
            model_data.capability_ranks.math,
            model_data.capability_ranks.code,
            model_data.capability_ranks.if_rank,
            model_data.capability_ranks.expert,
            model_data.capability_ranks.safety
        ]
        # 更新到模型能力矩阵
        import uuid
        model_id = f"model_{uuid.uuid4().hex}"

        capability_service.update_model_matrix(model_data.name, ranks_dict)
        print("Updated capability matrix after model registration.")
        # 2.注册模型到数据库
        

        # 对于模型的能力向量，在更新完模型能力矩阵后获取
        model_ability_vector = capability_service.get_model_ability_vector(model_data.name)
        db_model = Model(
            id=model_id,
            name=model_data.name,
            capability_ranks=model_data.capability_ranks.model_dump(), # 模型排名
            capability_vector=model_ability_vector, #模型能力向量
            max_tokens=model_data.max_tokens,
            avg_latency_ms=model_data.avg_latency_ms,
            cost_per_1k_usd=model_data.cost_per_1k_usd,
            stake_eth=model_data.stake_eth
        )
        print(111)
        # 3. 前端得到成功后刷新页面即可，不需要在这里返回modelInfo
        return ApiResponse(
                success=True,
                message="模型注册成功",
                data=ModelInfo(
                    id=db_model.id,
                    name=db_model.name,
                    capability_ranks=CapabilityRanks.from_list(db_model.capability_ranks),
                    capability_vector=db_model.capability_vector,
                    max_tokens=db_model.max_tokens,
                    avg_latency_ms=db_model.avg_latency_ms,
                    cost_per_1k_usd=db_model.cost_per_1k_usd,
                    stake_eth=db_model.stake_eth,
                    is_verified=db_model.is_verified,
                    trust_score=db_model.trust_score,
                    registration_time=db_model.registration_time,
                    violations=db_model.violations
                )
            )
    except Exception as e:
        db.rollback()
        print(e)
        return ApiResponse(
            success=False,
            message="模型注册失败: " + str(e),
            data=None
        )

@app.get("/api/models")
async def get_models(db: Session = Depends(get_db)):
    """
    获取模型列表
    """
    try:
        models = db.query(Model).all()
        print(len(models))
        return ApiResponse(
            success=True,
            message="获取模型列表成功",
            data=[
                ModelInfo(
                    id=model.id,
                    name=model.name,
                    capability_ranks=CapabilityRanks.from_list(model.capability_ranks),
                    capability_vector=model.capability_vector,
                    max_tokens=model.max_tokens,
                    avg_latency_ms=model.avg_latency_ms,
                    cost_per_1k_usd=model.cost_per_1k_usd,
                    stake_eth=model.stake_eth,
                    is_verified=model.is_verified,
                    trust_score=model.trust_score,
                    registration_time=model.registration_time,
                    violations=model.violations
                ) for model in models]
        )
    except Exception as e:
        return ApiResponse(
            success=False, 
            message="获取模型列表失败"+ str(e),
            data={
                "error": str(e)
            }
        )
    
@app.get("/api/models/{model_id}", response_model=ModelInfo)
async def get_model(model_id: str, db: Session = Depends(get_db)):
    """
    获取具体模型的信息
    """
    model = db.query(Model).filter(Model.id == model_id).first()
    try:
        if not model:
            # 理论上不存在，因为前端获取模型信息应该点击存在的模型
            return ApiResponse(
                success=False,
                message="模型不存在",
                data={
                    "model_id": model_id
                }
            )

        return ApiResponse(
            success=True,
            message="获取模型信息成功",
            data=ModelInfo(
                id=model.id,
                name=model.name,
                capability_ranks=CapabilityRanks(**model.capability_ranks),
                capability_vector=model.capability_vector,
                max_tokens=model.max_tokens,
                avg_latency_ms=model.avg_latency_ms,
                cost_per_1k_usd=model.cost_per_1k_usd,
                stake_eth=model.stake_eth,
                is_verified=model.is_verified,
                trust_score=model.trust_score,
                registration_time=model.registration_time,
                violations=model.violations
            )
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message="获取模型信息失败",
            data={
                "error": str(e)
            }
        )

@app.post("/api/models/{model_id}/verify")
async def verify_model(model_id: str, db: Session = Depends(get_db)):
    """
    验证模型能力，需要区块链接入
    """
    # model = db.query(Model).filter(Model.id == model_id).first()
    # if not model:
    #     raise HTTPException(status_code=404, detail="Model not found")

    # # Verify on blockchain
    # blockchain.verify_model(model_id)

    # # Update database
    # model.is_verified = True
    # db.commit()

    # return {"success": True, "model_id": model_id, "is_verified": True}
    return ApiResponse(
        success=True,
        message="模型验证成功",
        data={
            "model_id": model_id
        }
    )

# ============ chat and routing ============
@app.post("/api/chat")
async def get_all_conversations(
    db: Session = Depends(get_db)
):
    """
    Get all conversations from the database
    """
    try:
        conversation_ids = memory_manager.get_all_conversations(db=db)
        return ApiResponse(
            success=True,
            message="获取会话成功",
            data={"conversation_ids": conversation_ids}
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message="获取会话失败",
            data={
                "error": str(e)
            }
        )

@app.post("/api/chat/register-conversation")
async def register_conversation(
    db: Session = Depends(get_db)
):
    """
    Register a new conversation
    """
    try:
        memory_manager.register_conversation(db=db)
        return ApiResponse(
            success=True,
            message="注册会话成功", 
            data={
                
            }
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message="注册会话失败",
            data={
                "error": str(e)
            }
        )

@app.post("/api/route/get-conversation")
async def get_memory(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get all memories from the vector database
    every time when user opens a new session, we load all memories from vector db
    """
    try:
        memories_history = memory_manager.load_existing_memories(conversation_id=conversation_id, db=db)
        return ApiResponse(
            success=True,
            message="获取记忆成功",
            data={
                "memories": memories_history
            }
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message="获取记忆失败",
            data={
                "error": str(e)
            }
        )

@app.post("/api/chat/route")
async def get_response(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Route a user query to the best available model
    return the answer 
    """
    try:
        query = request.get("query", "")
        rewrite_query = memory_manager.rewrite_query(query, db)
        res_model = router.route_query(query) # use orginal query to route beacause the rewrite may change the meaning
        response = router.get_response_from_model(rewrite_query, res_model)
        return ApiResponse(
            success=True,
            message="路由成功",
            data={
                "response": response,
                "model_name": res_model[0] if res_model else None
            }
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message="路由失败",
            data={
                "error": str(e)
            }
        )
    
@app.get("/api/routing/stats")
async def get_routing_stats(hours: int = 24):
    """Get routing statistics"""
    return ApiResponse(
        success=True,
        message="获取路由统计成功",
        data=None
    )

@app.post("/api/routing/commit-batch")
async def commit_routing_batch(period: str):
    """Commit a batch of routing decisions to blockchain"""
    return ApiResponse(
        success=True,
        message="提交路由批次成功",
        data=router.commit_routing_batch(period)
    )

# ============ Performance Tracking Endpoints ============

@app.post("/api/performance/report")
async def report_performance(
    report: PerformanceReport,
    db: Session = Depends(get_db)
):
    """Report model performance metrics"""
    # try:
    #     # Report to blockchain
    #     tx_hash = blockchain.report_performance(report.dict())

    #     # Store in database
    #     db_record = PerformanceRecord(
    #         model_id=report.model_id,
    #         period=report.period,
    #         avg_latency_ms=report.avg_latency_ms,
    #         success_rate=report.success_rate,
    #         uptime_percentage=report.uptime_percentage,
    #         violations=report.violations
    #     )
    #     db.add(db_record)
    #     db.commit()

    #     return {
    #         "success": True,
    #         "transaction_hash": tx_hash,
    #         "model_id": report.model_id
    #     }
    # except Exception as e:
    #     db.rollback()
    #     raise HTTPException(status_code=500, detail=str(e))
    return ApiResponse(
        success=True,
        message="性能报告成功",
        data={
            "model_id": report.model_id,
            "period": report.period
        }
    )

@app.get("/api/performance/{model_id}")
async def get_model_performance(model_id: str, limit: int = 100):
    """Get performance records for a specific model"""
    # records = blockchain.get_performance_records(model_id, limit)
    # return {
    #     "model_id": model_id,
    #     "records": records,
    #     "count": len(records)
    # }
    return ApiResponse(
        success=True,
        message="获取模型性能成功",
        data={}
    )


# ============ Violation Reporting Endpoints ============

@app.post("/api/violations/report")
async def report_violation(
    violation: ViolationReport,
    db: Session = Depends(get_db)
):
    """Report a model violation"""
    # try:
    #     # Report to blockchain
    #     tx_hash = blockchain.report_violation(violation.dict())

    #     # Store in database
    #     db_record = ViolationRecord(
    #         model_id=violation.model_id,
    #         issue=violation.issue,
    #         severity=violation.severity,
    #         slash_amount_eth=violation.slash_amount_eth
    #     )
    #     db.add(db_record)
    #     db.commit()

    #     # Update model's violation count and trust score
    #     model = db.query(Model).filter(Model.id == violation.model_id).first()
    #     if model:
    #         model.violations += 1
    #         model.trust_score = max(0, model.trust_score - 10)  # Reduce trust score
    #         db.commit()

    #     return {
    #         "success": True,
    #         "transaction_hash": tx_hash,
    #         "model_id": violation.model_id,
    #         "slash_amount": violation.slash_amount_eth
    #     }
    # except Exception as e:
    #     db.rollback()
    #     raise HTTPException(status_code=500, detail=str(e))
    return ApiResponse(
        success=True,
        message="违规报告成功",
        data={
            "model_id": violation.model_id,
            "issue": violation.issue,
            "severity": violation.severity,
            "slash_amount": violation.slash_amount_eth
        }
    )

@app.get("/api/violations/{model_id}")
async def get_model_violations(model_id: str, limit: int = 100):
    """Get violation records for a specific model"""
    # records = blockchain.get_violation_records(model_id, limit)
    # return {
    #     "model_id": model_id,
    #     "records": records,
    #     "count": len(records)
    # }
    return ApiResponse(
        success=True,
        message="获取模型违规记录成功",
        data={}
    )



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
