
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn

from models import (
    ModelRegistration, ModelInfo, RoutingDecision, RoutingBatch,
    PerformanceReport, ViolationReport, TrustScoreUpdate, CapabilityRanks
)
# from blockchain_service import blockchain
from router_service import router
from capability_service import capability_service
from database import init_db, get_db, Model, RoutingRecord, PerformanceRecord, ViolationRecord
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

# ============ Model Registry Endpoints ============

@app.post("/api/models/register", response_model=ModelInfo)
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
        capability_service.update_model_matrix(model_data.name, ranks_dict)

        # 2.注册模型到数据库
        import uuid
        model_id = f"model_{uuid.uuid4().hex}"

        # 对于模型的能力向量，在更新完模型能力矩阵后获取
        model_ability_vector = capability_service.get_model_vector(model_data.name)
        db_model = Model(
            id=model_id,
            name=model_data.name,
            capability_ranks=model_data.capability_ranks, # 模型排名
            capability_vector=model_ability_vector, #模型能力向量
            max_tokens=model_data.max_tokens,
            avg_latency_ms=model_data.avg_latency_ms,
            cost_per_1k_usd=model_data.cost_per_1k_usd,
            stake_eth=model_data.stake_eth
        )
        db.add(db_model)
        db.commit()
        db.refresh(db_model)

        # 3. 前端得到成功后刷新页面即可，不需要在这里返回modelInfo
        return ApiResponse(
            status="success",
            message="模型注册成功",
            data={
                "model_id": model_id,
                "model_name": model_data.name
            }
            )
    except Exception as e:
        db.rollback()
        return ApiResponse(
            status="error",
            message="模型注册失败",
            data={
                "error": str(e)
            }
        )

@app.get("/api/models", response_model=List[ModelInfo])
async def get_models(db: Session = Depends(get_db)):
    """
    获取模型列表
    """
    try:
        models = db.query(Model).all()
        return ApiResponse(
            status="success",
            message="获取模型列表成功",
            data=[ModelInfo(
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
            ) for model in models]
        )
    except Exception as e:
        return ApiResponse(
            status="error",
            message="获取模型列表失败",
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
                status="error",
                message="模型不存在",
                data={
                    "model_id": model_id
                }
            )

        return ModelInfo(
            id=model.id,
            name=model.name,
            capability_ranks=CapabilityRanks(**model.capability_ranks),
            capability_matrix=model.capability_vector,
            max_tokens=model.max_tokens,
            avg_latency_ms=model.avg_latency_ms,
            cost_per_1k_usd=model.cost_per_1k_usd,
            stake_eth=model.stake_eth,
            is_verified=model.is_verified,
            trust_score=model.trust_score,
            registration_time=model.registration_time,
            violations=model.violations
        )
    except Exception as e:
        return ApiResponse(
            status="error",
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
        status="success",
        message="模型验证成功",
        data={
            "model_id": model_id
        }
    )

# ============ Routing Endpoints ============

@app.post("/api/route")
async def route_query(
    query: str,
    capability: Optional[str] = None
):
    """Route a user query to the best available model"""
    result = router.route_query(query, capability)
    return result

@app.get("/api/routing/stats")
async def get_routing_stats(hours: int = 24):
    """Get routing statistics"""
    return router.get_routing_stats(hours)

@app.post("/api/routing/commit-batch")
async def commit_routing_batch(period: str):
    """Commit a batch of routing decisions to blockchain"""
    return router.commit_routing_batch(period)

# ============ Performance Tracking Endpoints ============

@app.post("/api/performance/report")
async def report_performance(
    report: PerformanceReport,
    db: Session = Depends(get_db)
):
    """Report model performance metrics"""
    try:
        # Report to blockchain
        tx_hash = blockchain.report_performance(report.dict())

        # Store in database
        db_record = PerformanceRecord(
            model_id=report.model_id,
            period=report.period,
            avg_latency_ms=report.avg_latency_ms,
            success_rate=report.success_rate,
            uptime_percentage=report.uptime_percentage,
            violations=report.violations
        )
        db.add(db_record)
        db.commit()

        return {
            "success": True,
            "transaction_hash": tx_hash,
            "model_id": report.model_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance/{model_id}")
async def get_model_performance(model_id: str, limit: int = 100):
    """Get performance records for a specific model"""
    records = blockchain.get_performance_records(model_id, limit)
    return {
        "model_id": model_id,
        "records": records,
        "count": len(records)
    }

# ============ Violation Reporting Endpoints ============

@app.post("/api/violations/report")
async def report_violation(
    violation: ViolationReport,
    db: Session = Depends(get_db)
):
    """Report a model violation"""
    try:
        # Report to blockchain
        tx_hash = blockchain.report_violation(violation.dict())

        # Store in database
        db_record = ViolationRecord(
            model_id=violation.model_id,
            issue=violation.issue,
            severity=violation.severity,
            slash_amount_eth=violation.slash_amount_eth
        )
        db.add(db_record)
        db.commit()

        # Update model's violation count and trust score
        model = db.query(Model).filter(Model.id == violation.model_id).first()
        if model:
            model.violations += 1
            model.trust_score = max(0, model.trust_score - 10)  # Reduce trust score
            db.commit()

        return {
            "success": True,
            "transaction_hash": tx_hash,
            "model_id": violation.model_id,
            "slash_amount": violation.slash_amount_eth
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/violations/{model_id}")
async def get_model_violations(model_id: str, limit: int = 100):
    """Get violation records for a specific model"""
    records = blockchain.get_violation_records(model_id, limit)
    return {
        "model_id": model_id,
        "records": records,
        "count": len(records)
    }

# ============ Trust Score Endpoints ============

@app.get("/api/trust-scores")
async def get_all_trust_scores(db: Session = Depends(get_db)):
    """Get trust scores for all models"""
    models = db.query(Model).all()
    return [
        {
            "model_id": m.id,
            "model_name": m.name,
            "trust_score": m.trust_score,
            "is_verified": m.is_verified,
            "violations": m.violations
        }
        for m in models
    ]

@app.get("/api/trust-scores/{model_id}")
async def get_model_trust_score(model_id: str, db: Session = Depends(get_db)):
    """Get trust score for a specific model"""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return {
        "model_id": model.id,
        "model_name": model.name,
        "trust_score": model.trust_score,
        "is_verified": model.is_verified,
        "violations": model.violations,
        "registration_time": model.registration_time,
        "capabilities": model.capabilities.split(",")
    }

# ============ Dashboard Endpoints ============

@app.get("/api/dashboard/overview")
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """Get dashboard overview data"""
    total_models = db.query(Model).count()
    verified_models = db.query(Model).filter(Model.is_verified == True).count()
    total_violations = db.query(ViolationRecord).count()

    # Get recent performance records
    recent_performance = db.query(PerformanceRecord).order_by(
        PerformanceRecord.report_time.desc()
    ).limit(10).all()

    # Get top models by trust score
    top_models = db.query(Model).order_by(
        Model.trust_score.desc()
    ).limit(5).all()

    return {
        "total_models": total_models,
        "verified_models": verified_models,
        "total_violations": total_violations,
        "recent_performance": [
            {
                "model_id": p.model_id,
                "period": p.period,
                "avg_latency_ms": p.avg_latency_ms,
                "success_rate": p.success_rate
            }
            for p in recent_performance
        ],
        "top_models": [
            {
                "model_id": m.id,
                "name": m.name,
                "trust_score": m.trust_score,
                "is_verified": m.is_verified
            }
            for m in top_models
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
