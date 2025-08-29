# Memory Catalog Architecture

## Overview
Replace memory injection with a catalog-based system where CIs request specific memories.

## Components

### 1. Apollo Memory Curator
- Maintains memory catalog/index
- Creates summaries and abstracts
- Manages memory lifecycle
- Provides search and retrieval APIs

### 2. Rhetor Token Optimizer  
- Manages token budgets per CI
- Optimizes memory presentation
- Prioritizes relevant memories
- Truncates/summarizes as needed

### 3. Memory Catalog Index
Instead of full memories, maintain lightweight index:
```python
{
    "memory_id": "uuid",
    "timestamp": "2025-08-29T10:00:00",
    "ci": "ergon",
    "type": "solution",
    "summary": "50 char summary",
    "abstract": "200 char abstract",
    "keywords": ["async", "python", "error"],
    "relevance_vector": [0.1, 0.2, ...],
    "size": 1500,  # tokens
    "tier": "medium"
}
```

### 4. Hook Interface API

#### Pre-Prompt Hook
```python
async def pre_prompt_hook(ci_name: str, prompt: str, context: dict):
    """Called before CI processes prompt"""
    # 1. Apollo analyzes prompt and context
    catalog = await apollo.get_memory_catalog(ci_name, prompt, context)
    
    # 2. Return catalog (not memories)
    return {
        "catalog": catalog,
        "token_budget": rhetor.get_token_budget(ci_name),
        "recommendation": apollo.recommend_memories(catalog, prompt)
    }
```

#### Memory Request Hook
```python
async def memory_request_hook(ci_name: str, memory_ids: List[str]):
    """CI requests specific memories from catalog"""
    # 1. Rhetor checks token budget
    if not rhetor.can_afford(ci_name, memory_ids):
        memory_ids = rhetor.prioritize(memory_ids)
    
    # 2. Apollo retrieves memories
    memories = await apollo.retrieve_memories(memory_ids)
    
    # 3. Rhetor optimizes presentation
    return rhetor.format_memories(memories, ci_name)
```

#### Post-Response Hook
```python
async def post_response_hook(ci_name: str, response: str, memories_used: List[str]):
    """After CI generates response"""
    # 1. Apollo learns which memories were useful
    await apollo.update_relevance(memories_used, response)
    
    # 2. Rhetor updates token usage
    rhetor.track_usage(ci_name, memories_used)
```

## Migration Path

### Phase 1: Catalog Creation
1. Convert existing memory_injector.py to catalog_builder.py
2. Build memory index from Engram data
3. Create Apollo curator service

### Phase 2: Hook Implementation  
1. Add hook points to CI handler
2. Implement catalog API
3. Add memory request interface

### Phase 3: CI Integration
1. Update CIs to use catalog API
2. Remove direct memory injection
3. Add memory selection logic to CIs

### Phase 4: Optimization
1. Implement Rhetor token optimization
2. Add relevance learning
3. Tune memory selection algorithms

## Benefits
1. **No Token Explosion** - CIs only get memories they request
2. **CI Autonomy** - CIs decide what memories they need
3. **Clean Boundaries** - Hooks at edges, CI remains black box
4. **Scalable** - Catalog can grow without impacting prompt size
5. **Learnable** - System learns which memories are useful

## Example Usage

```python
# In CI handler (black box)
class EnhancedCIHandler:
    async def process_prompt(self, prompt):
        # 1. Get memory catalog (lightweight)
        catalog_info = await self.pre_prompt_hook(self.name, prompt)
        
        # 2. CI decides what memories it wants
        needed_memories = self.select_memories(catalog_info['catalog'])
        
        # 3. Request specific memories
        if needed_memories:
            memories = await self.memory_request_hook(self.name, needed_memories)
            prompt = self.enrich_prompt(prompt, memories)
        
        # 4. Process normally
        response = await self.generate_response(prompt)
        
        # 5. Report usage
        await self.post_response_hook(self.name, response, needed_memories)
        
        return response
```

## Next Steps
1. Create Apollo memory curator module
2. Create Rhetor token optimizer module  
3. Define hook interface specification
4. Build catalog from existing memories
5. Integrate with one CI for testing (suggest Ergon-CI first)