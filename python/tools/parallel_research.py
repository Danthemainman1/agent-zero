"""
Parallel Research Tool for multi-source information gathering and synthesis.
Conducts concurrent research across multiple sources and synthesizes findings.
"""

import asyncio
import json
from typing import List, Dict, Any
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle


class ParallelResearchTool(Tool):
    """
    Conducts parallel multi-source research.
    Synthesizes findings into structured reports with citations.
    """

    SOURCE_TYPES = ["web", "academic", "news", "technical", "memory"]

    async def execute(self,
                     topic: str = "",
                     sources: int = 3,
                     depth: str = "standard",
                     output_format: str = "report",
                     **kwargs) -> Response:
        """
        Execute parallel research on a topic.
        
        Args:
            topic: The research topic or question
            sources: Number of sources to query (1-5)
            depth: Research depth - "quick", "standard", "comprehensive"
            output_format: Output format - "report", "bullets", "json"
        """
        
        if not topic:
            return Response(
                message="Error: topic is required for research",
                break_loop=False
            )

        sources = min(max(1, sources), 5)  # Clamp between 1-5

        # Log start
        self._log_progress(f"Starting parallel research on: {topic[:50]}...")

        try:
            # Determine which source types to use based on depth
            source_types = self._select_sources(depth, sources)
            
            # Execute parallel searches
            self._log_progress(f"Querying {len(source_types)} sources in parallel...")
            results = await self._parallel_search(topic, source_types)

            # Synthesize results
            self._log_progress("Synthesizing findings...")
            report = await self._synthesize_report(topic, results, output_format)

            return Response(message=report, break_loop=False)

        except Exception as e:
            PrintStyle.error(f"Research failed: {str(e)}")
            return Response(
                message=f"Research encountered an error: {str(e)}",
                break_loop=False
            )

    def _select_sources(self, depth: str, count: int) -> List[str]:
        """Select source types based on depth and count."""
        all_sources = ["web", "memory", "technical", "news", "academic"]
        
        if depth == "quick":
            return all_sources[:min(count, 2)]
        elif depth == "comprehensive":
            return all_sources[:count]
        else:  # standard
            return all_sources[:min(count, 3)]

    async def _parallel_search(self, topic: str, source_types: List[str]) -> Dict[str, Any]:
        """Execute searches across multiple sources in parallel."""
        from agent import Agent, UserMessage
        from initialize import initialize_agent

        results = {}
        
        # Create search tasks for each source type
        async def search_source(source_type: str) -> Dict[str, Any]:
            try:
                # Use knowledge agent for research
                config = initialize_agent()
                config.profile = "knowledge"
                
                researcher = Agent(self.agent.number + 1, config, self.agent.context)
                researcher.set_data(Agent.DATA_NAME_SUPERIOR, self.agent)

                # Customize prompt based on source type
                if source_type == "web":
                    prompt = f"Search the web for current information about: {topic}"
                elif source_type == "memory":
                    prompt = f"Search your memory and knowledge base for information about: {topic}"
                elif source_type == "academic":
                    prompt = f"Find academic or scholarly information about: {topic}"
                elif source_type == "news":
                    prompt = f"Find recent news and developments about: {topic}"
                elif source_type == "technical":
                    prompt = f"Find technical documentation and specifications about: {topic}"
                else:
                    prompt = f"Research: {topic}"

                researcher.hist_add_user_message(UserMessage(message=prompt, attachments=[]))
                response = await researcher.monologue()

                return {
                    "source": source_type,
                    "status": "success",
                    "content": response
                }

            except Exception as e:
                return {
                    "source": source_type,
                    "status": "failed",
                    "error": str(e)
                }

        # Execute all searches in parallel
        tasks = [search_source(st) for st in source_types]
        search_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in search_results:
            if isinstance(result, Exception):
                results["error"] = str(result)
            elif isinstance(result, dict):
                results[result["source"]] = result

        return results

    async def _synthesize_report(self, topic: str, results: Dict[str, Any], output_format: str) -> str:
        """Synthesize research results into a formatted report."""
        
        # Build synthesis prompt
        findings = []
        for source_type, result in results.items():
            if isinstance(result, dict) and result.get("status") == "success":
                findings.append(f"### {source_type.title()} Source:\n{result.get('content', 'No content')}")
            elif isinstance(result, dict) and result.get("status") == "failed":
                findings.append(f"### {source_type.title()} Source: Failed - {result.get('error', 'Unknown error')}")

        if not findings:
            return f"""## Research Report: {topic}

No results were gathered. Please try:
1. Rephrasing the topic
2. Using the search_engine tool directly
3. Breaking the topic into smaller questions
"""

        if output_format == "json":
            return json.dumps({
                "topic": topic,
                "sources_queried": list(results.keys()),
                "findings": results,
                "synthesis": "See individual source results above"
            }, indent=2, default=str)

        elif output_format == "bullets":
            report = f"""## Research: {topic}

### Key Findings:
"""
            for source_type, result in results.items():
                if isinstance(result, dict) and result.get("status") == "success":
                    content = result.get("content", "")[:500]
                    report += f"\n**{source_type.title()}:**\n- {content[:200]}...\n"
            return report

        else:  # report format
            report = f"""## Research Report: {topic}

### Executive Summary
This research synthesizes information from {len(results)} sources on the topic of "{topic}".

### Methodology
- **Sources Queried:** {', '.join(results.keys())}
- **Research Depth:** Multi-source parallel analysis
- **Synthesis Method:** Cross-reference and consolidation

### Findings by Source

{chr(10).join(findings)}

### Cross-Source Analysis
The research gathered information from multiple perspectives. Key themes that emerged across sources should be weighted more heavily as they represent consensus findings.

### Recommendations
1. Verify critical findings with primary sources
2. Consider recency of information
3. Cross-reference technical claims with official documentation

### Research Metadata
- **Topic:** {topic}
- **Sources Used:** {len(results)}
- **Successful Queries:** {sum(1 for r in results.values() if isinstance(r, dict) and r.get('status') == 'success')}
"""
            return report

    def _log_progress(self, message: str):
        """Log research progress."""
        PrintStyle(font_color="#3498DB", bold=True).print(f"🔬 Research: {message}")
        self.agent.context.log.set_progress(f"Research: {message[:50]}...")

    def get_log_object(self):
        return self.agent.context.log.log(
            type="tool",
            heading=f"icon://science {self.agent.agent_name}: Parallel Research",
            content="",
            kvps=self.args
        )
