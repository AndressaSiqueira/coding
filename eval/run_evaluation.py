"""
Dynamic Agent Evaluation Script for Azure AI Foundry

This script:
1. Loads test cases from dataset.json
2. Invokes the deployed agent with each query
3. Evaluates responses using Azure AI Foundry evaluators
4. Checks against quality thresholds
"""

import os
import sys
import json
import time
import logging
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai.types.eval_create_params import DataSourceConfigCustom
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileID,
)

# Configure logging
timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def load_dataset(dataset_path: str) -> dict:
    """Load the evaluation dataset from JSON file."""
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def invoke_agent(project_client: AIProjectClient, agent_name: str, query: str, context: str = "", agent_id: str = None) -> str:
    """Invoke the deployed agent and get a response."""
    try:
        # Use agent ID directly if provided (preferred method)
        if agent_id:
            logger.info(f"Using agent ID directly: {agent_id}")
            try:
                agent = project_client.agents.get(agent_id)
                logger.info(f"Found agent: ID={agent.id}, Name='{agent.name}'")
            except Exception as e:
                logger.error(f"Failed to get agent by ID '{agent_id}': {e}")
                agent = None
        else:
            # Fallback: Get the agent by name
            agents_list = list(project_client.agents.list())
            
            # Log all available agents for debugging
            if agents_list:
                logger.info(f"Available agents in project ({len(agents_list)} total):")
                for a in agents_list:
                    logger.info(f"  - ID: {a.id}, Name: '{a.name}', Model: {getattr(a, 'model', 'N/A')}")
            else:
                logger.warning("No agents found in project!")
            
            # Try exact match first
            agent = next((a for a in agents_list if a.name == agent_name), None)
            
            # If not found, try case-insensitive match
            if not agent:
                agent = next((a for a in agents_list if a.name.lower() == agent_name.lower()), None)
                if agent:
                    logger.info(f"Found agent with case-insensitive match: '{agent.name}'")
        
        if not agent:
            logger.error(f"Agent '{agent_name}' (ID: {agent_id}) not found!")
            logger.error("Run will use mock responses which will fail quality checks.")
            return f"Mock response for: {query}"
        
        # Create a thread and run the agent
        thread = project_client.agents.threads.create()
        
        # Add user message with context
        message_content = f"Context: {context}\n\nQuestion: {query}" if context else query
        project_client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=message_content
        )
        
        # Run the agent
        run = project_client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        # Get assistant response
        messages = project_client.agents.messages.list(thread_id=thread.id)
        for msg in reversed(list(messages)):
            if msg.role == "assistant":
                if msg.content and len(msg.content) > 0:
                    return msg.content[0].text.value
        
        return "No response from agent"
        
    except Exception as e:
        logger.error(f"Error invoking agent: {e}")
        return f"Error: {str(e)}"


def create_evaluation_jsonl(test_cases: list, responses: list) -> str:
    """Create a JSONL file with queries and responses for evaluation."""
    temp_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    )
    
    for i, tc in enumerate(test_cases):
        record = {
            "query": tc["query"],
            "response": responses[i],
            "context": tc.get("context", ""),
        }
        temp_file.write(json.dumps(record) + "\n")
    
    temp_file.close()
    return temp_file.name


def run_evaluation(
    project_client: AIProjectClient,
    openai_client,
    dataset_file: str,
    model_deployment: str,
    evaluators: list[str],
) -> dict:
    """Run evaluation using Azure AI Foundry."""
    
    # Upload dataset
    logger.info("Uploading evaluation dataset...")
    dataset = project_client.datasets.upload_file(
        name=f"agent-eval-data-{timestamp}",
        version="1",
        file_path=dataset_file,
    )
    logger.info(f"Dataset uploaded: {dataset.name} (ID: {dataset.id})")

    # Define data source config
    data_source_config = DataSourceConfigCustom(
        {
            "type": "custom",
            "item_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "response": {"type": "string"},
                    "context": {"type": "string"},
                },
                "required": ["query", "response"],
            },
            "include_sample_schema": True,
        }
    )

    # Build testing criteria from evaluators
    testing_criteria = []
    for evaluator in evaluators:
        criteria = {
            "type": "azure_ai_evaluator",
            "name": evaluator,
            "evaluator_name": f"builtin.{evaluator}",
            "initialization_parameters": {"deployment_name": model_deployment},
        }
        
        # Set appropriate data mappings based on evaluator type
        if evaluator in ["coherence", "relevance"]:
            criteria["data_mapping"] = {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            }
        elif evaluator == "groundedness":
            criteria["data_mapping"] = {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
                "context": "{{item.context}}",
            }
        elif evaluator == "fluency":
            criteria["data_mapping"] = {
                "response": "{{item.response}}",
            }
        
        testing_criteria.append(criteria)

    # Create evaluation
    logger.info("Creating evaluation...")
    evaluation = openai_client.evals.create(
        name=f"agent-quality-eval-{timestamp}",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    logger.info(f"Evaluation created: {evaluation.id}")

    # Run evaluation
    logger.info("Starting evaluation run...")
    run = openai_client.evals.runs.create(
        eval_id=evaluation.id,
        name=f"agent-quality-run-{timestamp}",
        data_source=CreateEvalJSONLRunDataSourceParam(
            type="jsonl",
            source=SourceFileID(type="file_id", id=dataset.id),
        ),
    )
    logger.info(f"Run created: {run.id}")

    # Wait for completion
    while run.status not in ["completed", "failed"]:
        run = openai_client.evals.runs.retrieve(run_id=run.id, eval_id=evaluation.id)
        logger.info(f"Status: {run.status}")
        time.sleep(5)

    logger.info(f"Evaluation Report URL: {run.report_url}")

    # Get results
    results = {"status": run.status, "report_url": run.report_url, "scores": {}}
    
    if run.status == "completed":
        output_items = list(
            openai_client.evals.runs.output_items.list(run_id=run.id, eval_id=evaluation.id)
        )
        
        # Calculate average scores for each evaluator
        for evaluator in evaluators:
            scores = []
            for item in output_items:
                if hasattr(item, "results") and item.results:
                    for result in item.results:
                        if hasattr(result, "name") and result.name == evaluator:
                            if hasattr(result, "score"):
                                scores.append(result.score)
            
            if scores:
                results["scores"][evaluator] = sum(scores) / len(scores)
    
    return results


def check_thresholds(scores: dict, thresholds: dict) -> tuple[bool, list[str]]:
    """Check if scores meet quality thresholds."""
    failures = []
    
    for metric, threshold in thresholds.items():
        if metric in scores:
            if scores[metric] < threshold:
                failures.append(
                    f"{metric}: {scores[metric]:.2f} < {threshold} (threshold)"
                )
        else:
            failures.append(f"{metric}: no score available")
    
    return len(failures) == 0, failures


def main():
    # Configuration from environment
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    model_deployment = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
    agent_name = os.environ.get("AGENT_NAME", "three-pillars-demo-agent")
    agent_id = os.environ.get("AGENT_ID")  # Direct agent ID (preferred)
    dataset_path = os.environ.get("EVAL_DATASET_PATH", "eval/dataset.json")
    
    if not endpoint:
        logger.error("AZURE_AI_PROJECT_ENDPOINT environment variable is required")
        sys.exit(1)
    
    if agent_id:
        logger.info(f"Using agent ID: {agent_id}")
    else:
        logger.warning("AGENT_ID not set, will search by name (slower)")
    
    # Load dataset
    logger.info(f"Loading dataset from {dataset_path}")
    dataset = load_dataset(dataset_path)
    
    test_cases = dataset.get("test_cases", [])
    evaluators = dataset.get("evaluators", ["coherence", "relevance", "fluency"])
    thresholds = dataset.get("quality_thresholds", {})
    
    logger.info(f"Found {len(test_cases)} test cases")
    logger.info(f"Evaluators: {evaluators}")
    logger.info(f"Thresholds: {thresholds}")
    
    # Initialize clients
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        # Step 1: Invoke agent for each test case
        logger.info("Invoking agent for each test case...")
        responses = []
        for i, tc in enumerate(test_cases):
            logger.info(f"Test case {i+1}/{len(test_cases)}: {tc['query'][:50]}...")
            response = invoke_agent(
                project_client,
                agent_name,
                tc["query"],
                tc.get("context", ""),
                agent_id=agent_id,
            )
            responses.append(response)
            logger.info(f"Response: {response[:100]}...")
        
        # Step 2: Create JSONL for evaluation
        logger.info("Creating evaluation dataset...")
        eval_file = create_evaluation_jsonl(test_cases, responses)
        
        try:
            # Step 3: Run evaluation
            results = run_evaluation(
                project_client,
                openai_client,
                eval_file,
                model_deployment,
                evaluators,
            )
            
            # Step 4: Check thresholds
            logger.info("=" * 60)
            logger.info("EVALUATION RESULTS")
            logger.info("=" * 60)
            
            for metric, score in results["scores"].items():
                threshold = thresholds.get(metric, 0)
                status = "✓" if score >= threshold else "✗"
                logger.info(f"{status} {metric}: {score:.2f} (threshold: {threshold})")
            
            passed, failures = check_thresholds(results["scores"], thresholds)
            
            if passed:
                logger.info("=" * 60)
                logger.info("✓ All quality thresholds met!")
                logger.info(f"Report: {results['report_url']}")
                sys.exit(0)
            else:
                logger.error("=" * 60)
                logger.error("✗ Quality thresholds not met:")
                for failure in failures:
                    logger.error(f"  - {failure}")
                logger.error(f"Report: {results['report_url']}")
                sys.exit(1)
                
        finally:
            # Cleanup temp file
            Path(eval_file).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
