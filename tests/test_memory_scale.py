#!/usr/bin/env python3
"""
Memory System Scale Testing
Tests memory system under high load and concurrent usage.
"""

import asyncio
import time
import random
import statistics
from typing import List, Dict, Any
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.memory.middleware import (
    MemoryMiddleware,
    MemoryConfig,
    InjectionStyle,
    MemoryTier
)
from shared.memory.collective import (
    CollectiveMemoryProtocol,
    ShareType,
    MemoryType
)
from shared.memory.clustering import SemanticClusterer, ClusterType
from shared.memory.optimizer import MemoryOptimizer
from shared.memory.metrics import get_memory_metrics


class ScaleTester:
    """Tests memory system at scale."""
    
    def __init__(self, num_cis: int = 10):
        self.num_cis = num_cis
        self.ci_middlewares = {}
        self.collective = CollectiveMemoryProtocol()
        self.metrics = get_memory_metrics()
        self.test_results = {}
        
    async def setup(self):
        """Set up test environment."""
        print(f"Setting up {self.num_cis} CI instances...")
        
        for i in range(self.num_cis):
            ci_name = f"test_ci_{i}"
            config = MemoryConfig(
                namespace=ci_name,
                injection_style=InjectionStyle.NATURAL,
                memory_tiers=[
                    MemoryTier.RECENT,
                    MemoryTier.SESSION,
                    MemoryTier.DOMAIN
                ]
            )
            self.ci_middlewares[ci_name] = MemoryMiddleware(config)
        
        print(f"✓ Created {self.num_cis} CI middleware instances")
    
    async def test_concurrent_storage(self, operations: int = 1000):
        """Test concurrent memory storage."""
        print(f"\nTesting concurrent storage ({operations} operations)...")
        
        async def store_memory(ci_name: str, index: int):
            """Store a single memory."""
            middleware = self.ci_middlewares[ci_name]
            memory = {
                'type': 'test',
                'content': f"Memory {index} from {ci_name}",
                'timestamp': datetime.now().isoformat(),
                'metadata': {
                    'index': index,
                    'ci': ci_name
                }
            }
            
            start = time.time()
            success = await middleware.store_interaction(memory)
            latency = (time.time() - start) * 1000
            
            return success, latency
        
        # Create storage tasks
        tasks = []
        ci_names = list(self.ci_middlewares.keys())
        
        for i in range(operations):
            ci_name = random.choice(ci_names)
            task = store_memory(ci_name, i)
            tasks.append(task)
        
        # Execute concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Analyze results
        successes = sum(1 for success, _ in results if success)
        latencies = [latency for _, latency in results]
        
        stats = {
            'total_operations': operations,
            'successful': successes,
            'success_rate': successes / operations,
            'total_time': total_time,
            'throughput': operations / total_time,
            'avg_latency': statistics.mean(latencies),
            'p50_latency': statistics.median(latencies),
            'p95_latency': statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else max(latencies),
            'p99_latency': statistics.quantiles(latencies, n=100)[98] if len(latencies) > 100 else max(latencies)
        }
        
        self.test_results['concurrent_storage'] = stats
        
        print(f"  Throughput: {stats['throughput']:.1f} ops/sec")
        print(f"  Success rate: {stats['success_rate']:.1%}")
        print(f"  Avg latency: {stats['avg_latency']:.1f}ms")
        print(f"  P95 latency: {stats['p95_latency']:.1f}ms")
    
    async def test_concurrent_retrieval(self, queries: int = 1000):
        """Test concurrent memory retrieval."""
        print(f"\nTesting concurrent retrieval ({queries} queries)...")
        
        # First store some memories
        await self._seed_memories(100)
        
        async def retrieve_memories(ci_name: str, query: str):
            """Retrieve memories."""
            middleware = self.ci_middlewares[ci_name]
            
            start = time.time()
            context = await middleware.get_memory_context(query)
            latency = (time.time() - start) * 1000
            
            result_count = (
                len(context.recent) +
                len(context.session) +
                len(context.domain)
            )
            
            return result_count, latency
        
        # Create retrieval tasks
        tasks = []
        ci_names = list(self.ci_middlewares.keys())
        queries_list = [
            "test", "memory", "data", "analysis",
            "pattern", "insight", "context", "information"
        ]
        
        for i in range(queries):
            ci_name = random.choice(ci_names)
            query = random.choice(queries_list)
            task = retrieve_memories(ci_name, query)
            tasks.append(task)
        
        # Execute concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Analyze results
        result_counts = [count for count, _ in results]
        latencies = [latency for _, latency in results]
        
        stats = {
            'total_queries': queries,
            'total_time': total_time,
            'throughput': queries / total_time,
            'avg_results': statistics.mean(result_counts) if result_counts else 0,
            'avg_latency': statistics.mean(latencies),
            'p50_latency': statistics.median(latencies),
            'p95_latency': statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else max(latencies),
            'p99_latency': statistics.quantiles(latencies, n=100)[98] if len(latencies) > 100 else max(latencies)
        }
        
        self.test_results['concurrent_retrieval'] = stats
        
        print(f"  Throughput: {stats['throughput']:.1f} queries/sec")
        print(f"  Avg results: {stats['avg_results']:.1f} memories/query")
        print(f"  Avg latency: {stats['avg_latency']:.1f}ms")
        print(f"  P95 latency: {stats['p95_latency']:.1f}ms")
    
    async def test_collective_sharing(self, shares: int = 500):
        """Test collective memory sharing at scale."""
        print(f"\nTesting collective sharing ({shares} shares)...")
        
        # Create sharing channel
        ci_names = list(self.ci_middlewares.keys())
        await self.collective.create_memory_channel(
            "scale_test",
            ci_names,
            MemoryType.COLLABORATION
        )
        
        async def share_memory(from_ci: str, to_cis: List[str]):
            """Share a memory."""
            memory = {
                'type': 'shared',
                'content': f"Shared insight from {from_ci}",
                'timestamp': datetime.now().isoformat()
            }
            
            start = time.time()
            memory_id = await self.collective.share_memory(
                memory,
                from_ci,
                to_cis,
                ShareType.BROADCAST,
                MemoryType.INSIGHT
            )
            latency = (time.time() - start) * 1000
            
            return memory_id is not None, latency
        
        # Create sharing tasks
        tasks = []
        
        for i in range(shares):
            from_ci = random.choice(ci_names)
            to_cis = random.sample(
                [ci for ci in ci_names if ci != from_ci],
                k=random.randint(1, min(5, len(ci_names) - 1))
            )
            task = share_memory(from_ci, to_cis)
            tasks.append(task)
        
        # Execute concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Analyze results
        successes = sum(1 for success, _ in results if success)
        latencies = [latency for _, latency in results]
        
        stats = {
            'total_shares': shares,
            'successful': successes,
            'success_rate': successes / shares,
            'total_time': total_time,
            'throughput': shares / total_time,
            'avg_latency': statistics.mean(latencies),
            'p95_latency': statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else max(latencies)
        }
        
        self.test_results['collective_sharing'] = stats
        
        print(f"  Throughput: {stats['throughput']:.1f} shares/sec")
        print(f"  Success rate: {stats['success_rate']:.1%}")
        print(f"  Avg latency: {stats['avg_latency']:.1f}ms")
    
    async def test_clustering_performance(self, memories_count: int = 1000):
        """Test clustering performance with large datasets."""
        print(f"\nTesting clustering performance ({memories_count} memories)...")
        
        # Generate test memories
        memories = []
        for i in range(memories_count):
            memories.append({
                'id': f'mem_{i}',
                'content': f"Test memory {i % 50}",  # Create natural clusters
                'timestamp': (datetime.now() - timedelta(minutes=i)).isoformat(),
                'metadata': {'index': i}
            })
        
        # Test clustering
        clusterer = SemanticClusterer("test_ci")
        
        start_time = time.time()
        clusters = await clusterer.cluster_memories(memories, ClusterType.SEMANTIC)
        clustering_time = time.time() - start_time
        
        stats = {
            'memories_count': memories_count,
            'clusters_created': len(clusters),
            'clustering_time': clustering_time,
            'memories_per_second': memories_count / clustering_time,
            'avg_cluster_size': statistics.mean(c.size() for c in clusters) if clusters else 0,
            'avg_coherence': statistics.mean(c.coherence for c in clusters) if clusters else 0
        }
        
        self.test_results['clustering'] = stats
        
        print(f"  Clusters created: {stats['clusters_created']}")
        print(f"  Clustering time: {stats['clustering_time']:.2f}s")
        print(f"  Processing rate: {stats['memories_per_second']:.0f} memories/sec")
        print(f"  Avg cluster size: {stats['avg_cluster_size']:.1f}")
        print(f"  Avg coherence: {stats['avg_coherence']:.2f}")
    
    async def test_optimization_impact(self):
        """Test impact of optimization on performance."""
        print(f"\nTesting optimization impact...")
        
        # Test before optimization
        ci_name = list(self.ci_middlewares.keys())[0]
        
        # Measure baseline
        baseline_latencies = []
        for _ in range(100):
            start = time.time()
            await self.ci_middlewares[ci_name].get_memory_context("test")
            baseline_latencies.append((time.time() - start) * 1000)
        
        baseline_avg = statistics.mean(baseline_latencies)
        
        # Run optimization
        optimizer = MemoryOptimizer(ci_name)
        optimization_result = await optimizer.optimize()
        
        # Measure after optimization
        optimized_latencies = []
        for _ in range(100):
            start = time.time()
            await self.ci_middlewares[ci_name].get_memory_context("test")
            optimized_latencies.append((time.time() - start) * 1000)
        
        optimized_avg = statistics.mean(optimized_latencies)
        
        stats = {
            'baseline_latency': baseline_avg,
            'optimized_latency': optimized_avg,
            'improvement': (baseline_avg - optimized_avg) / baseline_avg if baseline_avg > 0 else 0,
            'health_improvement': optimization_result.get('improvement', 0)
        }
        
        self.test_results['optimization'] = stats
        
        print(f"  Baseline latency: {stats['baseline_latency']:.1f}ms")
        print(f"  Optimized latency: {stats['optimized_latency']:.1f}ms")
        print(f"  Performance improvement: {stats['improvement']:.1%}")
        print(f"  Health improvement: {stats['health_improvement']:.1f}%")
    
    async def test_memory_growth(self, duration_seconds: int = 30):
        """Test memory system behavior over time."""
        print(f"\nTesting memory growth over {duration_seconds}s...")
        
        ci_name = list(self.ci_middlewares.keys())[0]
        middleware = self.ci_middlewares[ci_name]
        
        memory_counts = []
        latencies = []
        
        start_time = time.time()
        operation_count = 0
        
        while time.time() - start_time < duration_seconds:
            # Store memory
            memory = {
                'type': 'growth_test',
                'content': f"Memory at {operation_count}",
                'timestamp': datetime.now().isoformat()
            }
            
            op_start = time.time()
            await middleware.store_interaction(memory)
            latencies.append((time.time() - op_start) * 1000)
            
            operation_count += 1
            
            # Small delay to simulate realistic usage
            await asyncio.sleep(0.01)
        
        elapsed = time.time() - start_time
        
        stats = {
            'duration': elapsed,
            'operations': operation_count,
            'rate': operation_count / elapsed,
            'avg_latency': statistics.mean(latencies),
            'latency_trend': 'stable' if statistics.stdev(latencies) < 10 else 'increasing'
        }
        
        self.test_results['memory_growth'] = stats
        
        print(f"  Operations: {stats['operations']}")
        print(f"  Rate: {stats['rate']:.1f} ops/sec")
        print(f"  Avg latency: {stats['avg_latency']:.1f}ms")
        print(f"  Latency trend: {stats['latency_trend']}")
    
    async def _seed_memories(self, count: int):
        """Seed memories for testing."""
        for ci_name, middleware in self.ci_middlewares.items():
            for i in range(count // self.num_cis):
                memory = {
                    'type': 'seed',
                    'content': f"Seed memory {i} for {ci_name}",
                    'timestamp': datetime.now().isoformat()
                }
                await middleware.store_interaction(memory)
    
    def generate_report(self):
        """Generate scale test report."""
        print("\n" + "=" * 60)
        print("SCALE TEST REPORT")
        print("=" * 60)
        
        # Overall performance
        print("\n📊 Overall Performance:")
        
        if 'concurrent_storage' in self.test_results:
            storage = self.test_results['concurrent_storage']
            print(f"  Storage: {storage['throughput']:.0f} ops/sec @ {storage['p95_latency']:.0f}ms P95")
        
        if 'concurrent_retrieval' in self.test_results:
            retrieval = self.test_results['concurrent_retrieval']
            print(f"  Retrieval: {retrieval['throughput']:.0f} queries/sec @ {retrieval['p95_latency']:.0f}ms P95")
        
        if 'collective_sharing' in self.test_results:
            sharing = self.test_results['collective_sharing']
            print(f"  Sharing: {sharing['throughput']:.0f} shares/sec @ {sharing['avg_latency']:.0f}ms avg")
        
        if 'clustering' in self.test_results:
            clustering = self.test_results['clustering']
            print(f"  Clustering: {clustering['memories_per_second']:.0f} memories/sec")
        
        # SLA compliance
        print("\n✅ SLA Compliance:")
        sla_met = True
        
        for test_name, results in self.test_results.items():
            if 'p95_latency' in results:
                if results['p95_latency'] < 200:
                    print(f"  {test_name}: ✓ P95 < 200ms")
                else:
                    print(f"  {test_name}: ✗ P95 = {results['p95_latency']:.0f}ms")
                    sla_met = False
        
        # Recommendations
        print("\n💡 Recommendations:")
        
        if sla_met:
            print("  System performing within SLA targets")
        else:
            print("  Consider optimization for operations exceeding SLA")
        
        if 'optimization' in self.test_results:
            opt = self.test_results['optimization']
            if opt['improvement'] > 0.1:
                print(f"  Optimization improved performance by {opt['improvement']:.0%}")
        
        return self.test_results


async def run_scale_tests():
    """Run complete scale test suite."""
    print("=" * 60)
    print("MEMORY SYSTEM SCALE TESTING")
    print("=" * 60)
    
    tester = ScaleTester(num_cis=5)
    
    # Setup
    await tester.setup()
    
    # Run tests
    await tester.test_concurrent_storage(operations=500)
    await tester.test_concurrent_retrieval(queries=500)
    await tester.test_collective_sharing(shares=250)
    await tester.test_clustering_performance(memories_count=500)
    await tester.test_optimization_impact()
    await tester.test_memory_growth(duration_seconds=10)
    
    # Generate report
    report = tester.generate_report()
    
    print("\n" + "=" * 60)
    print("SCALE TESTING COMPLETE")
    print("=" * 60)
    
    return report


if __name__ == "__main__":
    asyncio.run(run_scale_tests())