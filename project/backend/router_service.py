
from typing import Dict, List, Optional
from datetime import datetime
import json
from blockchain_service import blockchain

class RouterService:
    """
    Smart Router service that integrates with the blockchain trust layer.
    Routes user queries to the best available AI model based on trust scores and capabilities.
    """

    def __init__(self):
        self.router_model = None  # Will be loaded with your trained model
        self.routing_history = []
        self.load_router_model()

    def load_router_model(self):
        """
        Load the trained router model.
        In production, this would load your actual trained model.
        """
        # TODO: Load your trained router model here
        # Example: self.router_model = torch.load('your_router_model.pth')
        pass

    def route_query(self, user_query: str, required_capability: Optional[str] = None) -> Dict:
        """
        Route a user query to the best available model.

        Args:
            user_query: The user's query text
            required_capability: Optional specific capability required

        Returns:
            Dict containing routing decision and reasoning
        """
        # Get all verified models from blockchain
        all_models = blockchain.get_all_models()
        verified_models = [m for m in all_models if m['is_verified']]

        if not verified_models:
            return {
                'success': False,
                'error': 'No verified models available',
                'suggestion': 'Please register and verify models first'
            }

        # Filter models by capability if specified
        if required_capability:
            capable_models = [
                m for m in verified_models 
                if required_capability in m['capabilities']
            ]
        else:
            capable_models = verified_models

        if not capable_models:
            return {
                'success': False,
                'error': f'No verified models with capability: {required_capability}',
                'available_capabilities': list(set(
                    cap for m in verified_models for cap in m['capabilities']
                ))
            }

        # Select best model based on trust score and other factors
        selected_model = self._select_best_model(capable_models, user_query)

        # Record routing decision on blockchain
        routing_record = {
            'model_id': selected_model['id'],
            'model_name': selected_model['name'],
            'timestamp': datetime.utcnow().isoformat(),
            'user_query': user_query,
            'selected_reason': self._get_selection_reason(selected_model, capable_models)
        }

        tx_hash = blockchain.record_routing_decision(routing_record)
        self.routing_history.append(routing_record)

        return {
            'success': True,
            'model_id': selected_model['id'],
            'model_name': selected_model['name'],
            'trust_score': selected_model['trust_score'],
            'reason': routing_record['selected_reason'],
            'blockchain_tx': tx_hash,
            'estimated_latency': selected_model['avg_latency_ms'],
            'cost_per_1k': selected_model['cost_per_1k_usd']
        }

    def _select_best_model(self, models: List[Dict], query: str) -> Dict:
        """
        Select the best model from available options.

        Selection criteria:
        1. Trust score (primary)
        2. Capability match with query
        3. Latency
        4. Cost
        """
        # Sort models by trust score (descending)
        sorted_models = sorted(models, key=lambda m: m['trust_score'], reverse=True)

        # In production, use your trained model to make this decision
        # For now, we use a simple heuristic approach

        # Select top model, but occasionally test lower-ranked models
        # This helps discover new good models
        import random
        if random.random() < 0.05 and len(sorted_models) > 1:  # 5% chance to explore
            # Select from top 3 models randomly
            top_3 = sorted_models[:3]
            return random.choice(top_3)

        return sorted_models[0]

    def _get_selection_reason(self, selected_model: Dict, all_models: List[Dict]) -> str:
        """
        Generate human-readable explanation for model selection.
        """
        reasons = []

        # Trust score comparison
        avg_trust = sum(m['trust_score'] for m in all_models) / len(all_models)
        if selected_model['trust_score'] > avg_trust:
            reasons.append(f"High trust score ({selected_model['trust_score']:.1f}/100)")

        # Latency advantage
        avg_latency = sum(m['avg_latency_ms'] for m in all_models) / len(all_models)
        if selected_model['avg_latency_ms'] < avg_latency:
            reasons.append(f"Low latency ({selected_model['avg_latency_ms']}ms)")

        # Cost advantage
        avg_cost = sum(m['cost_per_1k_usd'] for m in all_models) / len(all_models)
        if selected_model['cost_per_1k_usd'] < avg_cost:
            reasons.append(f"Cost-effective (${selected_model['cost_per_1k_usd']:.4f}/1K)")

        # Capabilities
        if len(selected_model['capabilities']) > 2:
            reasons.append(f"Multi-capable ({', '.join(selected_model['capabilities'][:3])})")

        return '; '.join(reasons) if reasons else "Selected based on overall metrics"

    def get_routing_stats(self, hours: int = 24) -> Dict:
        """
        Get routing statistics for the specified time period.
        """
        cutoff_time = datetime.utcnow().timestamp() - (hours * 3600)

        recent_records = [
            r for r in self.routing_history 
            if datetime.fromisoformat(r['timestamp']).timestamp() > cutoff_time
        ]

        if not recent_records:
            return {
                'total_requests': 0,
                'unique_models': 0,
                'top_models': []
            }

        # Count requests per model
        model_counts = {}
        for record in recent_records:
            model_name = record['model_name']
            model_counts[model_name] = model_counts.get(model_name, 0) + 1

        # Sort by request count
        sorted_models = sorted(
            model_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            'total_requests': len(recent_records),
            'unique_models': len(model_counts),
            'top_models': [
                {'model': model, 'requests': count}
                for model, count in sorted_models[:5]
            ]
        }

    def commit_routing_batch(self, period: str) -> Dict:
        """
        Commit a batch of routing decisions to blockchain.
        """
        stats = self.get_routing_stats(hours=1)  # Last hour's stats

        # Calculate Merkle root of recent routing records
        cutoff_time = datetime.utcnow().timestamp() - 3600
        recent_records = [
            r for r in self.routing_history 
            if datetime.fromisoformat(r['timestamp']).timestamp() > cutoff_time
        ]

        merkle_root = blockchain.calculate_merkle_root(recent_records)

        batch_data = {
            'period': period,
            'total_requests': stats['total_requests'],
            'routing_merkle_root': merkle_root,
            'top_models': stats['top_models']
        }

        committed_root = blockchain.commit_routing_batch(batch_data)

        return {
            'success': True,
            'period': period,
            'merkle_root': committed_root,
            'total_requests': stats['total_requests'],
            'top_models': stats['top_models']
        }

# Global router service instance
router = RouterService()
