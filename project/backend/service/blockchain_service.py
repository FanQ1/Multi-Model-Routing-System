
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
import json

class BlockchainService:
    """
    Simulates blockchain interactions for ModelChain system.
    In production, this would interact with actual smart contracts.
    """

    def __init__(self):
        self.model_registry = {}  # Simulated on-chain model registry
        self.routing_records = []  # Simulated on-chain routing records
        self.performance_records = []  # Simulated on-chain performance records
        self.violation_records = []  # Simulated on-chain violation records

    def register_model(self, model_data: Dict) -> str:
        """
        Register a model on the blockchain with staking.
        Returns model ID.
        """
        model_id = self._generate_model_id(model_data['name'])

        # 从能力排名生成能力列表
        capability_ranks = model_data.get('capability_ranks', {})
        capabilities = self._generate_capabilities_from_ranks(capability_ranks)

        model_record = {
            'id': model_id,
            'name': model_data['name'],
            'capability_ranks': capability_ranks,
            'capability_matrix': model_data.get('capability_matrix', []),
            'capabilities': capabilities,
            'max_tokens': model_data['max_tokens'],
            'avg_latency_ms': model_data['avg_latency_ms'],
            'cost_per_1k_usd': model_data['cost_per_1k_usd'],
            'stake_eth': model_data['stake_eth'],
            'is_verified': False,
            'trust_score': 50.0,
            'registration_time': datetime.utcnow().isoformat(),
            'violations': 0,
            'block_number': len(self.model_registry) + 1,
            'transaction_hash': self._generate_tx_hash()
        }

        self.model_registry[model_id] = model_record
        return model_id

    def _generate_capabilities_from_ranks(self, ranks: Dict) -> List[str]:
        """
        根据能力排名生成能力列表

        Args:
            ranks: 能力排名字典

        Returns:
            能力列表
        """
        capabilities = []
        # 根据排名决定是否包含该能力
        # 排名前20的模型才被认为具有该能力
        if ranks.get('math', 100) <= 20:
            capabilities.append('math')
        if ranks.get('code', 100) <= 20:
            capabilities.append('code')
        if ranks.get('if', 100) <= 20:
            capabilities.append('IF')
        if ranks.get('expert', 100) <= 20:
            capabilities.append('expert')
        if ranks.get('safety', 100) <= 20:
            capabilities.append('safety')

        return capabilities if capabilities else ['general']

    def verify_model(self, model_id: str) -> bool:
        """
        Verify a model's capabilities after testing.
        """
        if model_id in self.model_registry:
            self.model_registry[model_id]['is_verified'] = True
            self.model_registry[model_id]['verification_time'] = datetime.utcnow().isoformat()
            return True
        return False

    def record_routing_decision(self, routing_data: Dict) -> str:
        """
        Record a routing decision on the blockchain.
        Returns transaction hash.
        """
        record = {
            'model_id': routing_data['model_id'],
            'model_name': routing_data['model_name'],
            'timestamp': routing_data['timestamp'],
            'user_query': routing_data['user_query'],
            'selected_reason': routing_data['selected_reason'],
            'block_number': len(self.routing_records) + 1,
            'transaction_hash': self._generate_tx_hash()
        }

        self.routing_records.append(record)
        return record['transaction_hash']

    def commit_routing_batch(self, batch_data: Dict) -> str:
        """
        Commit a batch of routing decisions to blockchain.
        Returns Merkle root hash.
        """
        batch_record = {
            'period': batch_data['period'],
            'total_requests': batch_data['total_requests'],
            'merkle_root': batch_data['routing_merkle_root'],
            'top_models': batch_data['top_models'],
            'block_number': len(self.routing_records) + 1,
            'transaction_hash': self._generate_tx_hash(),
            'commit_time': datetime.utcnow().isoformat()
        }

        self.routing_records.append(batch_record)
        return batch_record['merkle_root']

    def report_performance(self, performance_data: Dict) -> str:
        """
        Report model performance metrics.
        Returns transaction hash.
        """
        record = {
            'model_id': performance_data['model_id'],
            'period': performance_data['period'],
            'avg_latency_ms': performance_data['avg_latency_ms'],
            'success_rate': performance_data['success_rate'],
            'uptime_percentage': performance_data.get('uptime_percentage', 100.0),
            'violations': performance_data.get('violations', 0),
            'block_number': len(self.performance_records) + 1,
            'transaction_hash': self._generate_tx_hash(),
            'report_time': datetime.utcnow().isoformat()
        }

        self.performance_records.append(record)

        # Update trust score based on performance
        self._update_trust_score(performance_data['model_id'], record)

        return record['transaction_hash']

    def report_violation(self, violation_data: Dict) -> str:
        """
        Report a model violation and apply penalty.
        Returns transaction hash.
        """
        record = {
            'model_id': violation_data['model_id'],
            'issue': violation_data['issue'],
            'severity': violation_data['severity'],
            'slash_amount_eth': violation_data['slash_amount_eth'],
            'block_number': len(self.violation_records) + 1,
            'transaction_hash': self._generate_tx_hash(),
            'report_time': datetime.utcnow().isoformat()
        }

        self.violation_records.append(record)

        # Apply penalty to model
        if violation_data['model_id'] in self.model_registry:
            model = self.model_registry[violation_data['model_id']]
            model['violations'] += 1
            model['stake_eth'] -= violation_data['slash_amount_eth']

            # Reduce trust score based on violation severity
            penalty = {
                'HIGH': 15,
                'MEDIUM': 8,
                'LOW': 3
            }
            model['trust_score'] = max(0, model['trust_score'] - penalty[violation_data['severity']])

        return record['transaction_hash']

    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """
        Get model information from blockchain.
        """
        return self.model_registry.get(model_id)

    def get_all_models(self) -> List[Dict]:
        """
        Get all registered models.
        """
        return list(self.model_registry.values())

    def get_model_trust_score(self, model_id: str) -> Optional[float]:
        """
        Get current trust score for a model.
        """
        model = self.model_registry.get(model_id)
        return model['trust_score'] if model else None

    def get_routing_records(self, limit: int = 100) -> List[Dict]:
        """
        Get recent routing records.
        """
        return self.routing_records[-limit:]

    def get_performance_records(self, model_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Get performance records, optionally filtered by model.
        """
        if model_id:
            return [r for r in self.performance_records if r['model_id'] == model_id][-limit:]
        return self.performance_records[-limit:]

    def get_violation_records(self, model_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Get violation records, optionally filtered by model.
        """
        if model_id:
            return [r for r in self.violation_records if r['model_id'] == model_id][-limit:]
        return self.violation_records[-limit:]

    def calculate_merkle_root(self, items: List[Dict]) -> str:
        """
        Calculate Merkle root for a list of items.
        """
        if not items:
            return hashlib.sha256(b'').hexdigest()

        # Convert items to strings and hash them
        leaves = [hashlib.sha256(json.dumps(item, sort_keys=True).encode()).hexdigest() 
                 for item in items]

        # Build Merkle tree
        while len(leaves) > 1:
            if len(leaves) % 2 == 1:
                leaves.append(leaves[-1])  # Duplicate last leaf if odd

            new_level = []
            for i in range(0, len(leaves), 2):
                combined = leaves[i] + leaves[i + 1]
                new_level.append(hashlib.sha256(combined.encode()).hexdigest())

            leaves = new_level

        return leaves[0]

    def _generate_model_id(self, model_name: str) -> str:
        """Generate unique model ID."""
        return f"model_{model_name.lower().replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    def _generate_tx_hash(self) -> str:
        """Generate mock transaction hash."""
        return f"0x{hashlib.sha256(str(datetime.utcnow().timestamp()).encode()).hexdigest()}"

    def _update_trust_score(self, model_id: str, performance_record: Dict):
        """
        Update model trust score based on performance.
        Score calculation:
        - Performance (40%): Meets latency/quality promises
        - Reliability (30%): Uptime and success rate
        - Usage (20%): How often selected by router
        - Age (10%): How long in the system
        """
        if model_id not in self.model_registry:
            return

        model = self.model_registry[model_id]

        # Performance score (0-40)
        promised_latency = model['avg_latency_ms']
        actual_latency = performance_record['avg_latency_ms']
        latency_ratio = promised_latency / actual_latency if actual_latency > 0 else 1
        performance_score = min(40, 40 * latency_ratio)

        # Reliability score (0-30)
        success_rate = performance_record['success_rate']
        reliability_score = (success_rate / 100) * 30

        # Usage score (0-20) - based on recent routing selections
        recent_selections = sum(1 for r in self.routing_records[-100:] 
                               if r.get('model_id') == model_id)
        usage_score = min(20, recent_selections / 5)

        # Age score (0-10) - based on registration time
        registration_time = datetime.fromisoformat(model['registration_time'])
        days_registered = (datetime.utcnow() - registration_time).days
        age_score = min(10, days_registered / 30 * 10)

        # Calculate new trust score
        new_score = performance_score + reliability_score + usage_score + age_score

        # Smooth transition (weighted average with previous score)
        model['trust_score'] = (model['trust_score'] * 0.7) + (new_score * 0.3)
        model['trust_score'] = min(100, max(0, model['trust_score']))  # Clamp between 0 and 100

# Global blockchain service instance
blockchain = BlockchainService()
