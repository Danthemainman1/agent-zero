## Tool: "parallel_research" - Multi-Source Parallel Research

Use this tool to conduct comprehensive research by querying multiple sources simultaneously and synthesizing the findings.

### When to use:
- Research topics requiring multiple perspectives
- Gathering comprehensive information quickly
- Cross-referencing information from different sources
- Creating research reports with citations

### Arguments:
- **topic** (required): The research topic or question
- **sources** (optional): Number of sources to query (1-5, default: 3)
- **depth** (optional): Research depth
  - `"quick"` - Fast overview from 1-2 sources
  - `"standard"` - Balanced research from 2-3 sources (default)
  - `"comprehensive"` - Deep research from all available sources
- **output_format** (optional): Output format
  - `"report"` - Full structured report (default)
  - `"bullets"` - Bullet point summary
  - `"json"` - Structured JSON data

### Source Types Used:
- **web** - Current web information
- **memory** - Agent's knowledge base and memory
- **technical** - Technical documentation
- **news** - Recent news and developments
- **academic** - Scholarly and research sources

### Usage Examples:

**Standard research:**
```json
{
    "thoughts": ["I need to research this topic thoroughly from multiple angles..."],
    "tool_name": "parallel_research",
    "tool_args": {
        "topic": "The impact of large language models on software development",
        "sources": 3,
        "depth": "standard"
    }
}
```

**Quick overview:**
```json
{
    "thoughts": ["I need a quick overview of this topic..."],
    "tool_name": "parallel_research",
    "tool_args": {
        "topic": "Latest developments in quantum computing",
        "depth": "quick",
        "output_format": "bullets"
    }
}
```

**Comprehensive research:**
```json
{
    "thoughts": ["This requires deep research from all available sources..."],
    "tool_name": "parallel_research",
    "tool_args": {
        "topic": "Best practices for microservices architecture",
        "sources": 5,
        "depth": "comprehensive",
        "output_format": "report"
    }
}
```

### Best Practices:
1. Be specific with your topic for better results
2. Use "quick" depth for simple queries
3. Use "comprehensive" for important decisions
4. Cross-reference findings with direct searches when critical
5. Consider using orchestrate tool for very complex multi-topic research
