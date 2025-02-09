# ⚠️ Important Notice: This repository contains limited version of the final product. 
# We are currently withholding the full version due to its exceptional effectiveness 
# at discovering critical vulnerabilities in smart contracts. The full version will 
# be published after careful consideration of responsible disclosure practices.

from pathlib import Path
import sys
from typing import List, Set, Dict, Generator, Tuple, AsyncIterator
from dataclasses import dataclass

from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import logging
import asyncio
from typing import List, Dict, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(
    api_key=os.getenv("AI_API_KEY"),
    base_url=os.getenv("AI_BASE_URL"),
)

# Define auditor prompt as a single string
auditor_prompt = """
URGENT SECURITY AUDIT!

Analyze the following smart contract. Identify any critical vulnerability in the contract and provide a concise explanation of the issue.

Smart Contract:
{code}
"""

# Define critic prompt as a single string
critic_prompt = """
URGENT SECURITY VALIDATION!

Evaluate the vulnerability analysis provided below for the given smart contract.
Decide if the analysis correctly identifies a critical vulnerability.
Your response must end with either 'YES' if the analysis is valid or 'NO' if not.

Smart Contract:
{code}

Vulnerability analysis:
{analysis}
"""

@dataclass
class AuditTask:
    """Represents a single audit task"""
    category: str
    template: str
    code: str
    highlighted_section: str
    reference_id: str

@dataclass
class AuditIssue:
    """Represents a security issue found during the audit"""
    category: str
    description: str
    severity: str
    code_context: str
    is_validated_by_critic: bool = False

async def analyze_with_openai(prompt: str, category: str) -> Tuple[str, str]:
    """Send prompt to OpenAI and get response"""
    try:
        response = await client.chat.completions.create(
            model=os.getenv("AI_MODEL"),
            messages=[
                {"role": "system", "content": "You are an expert smart contract security auditor. Your task is to find critical vulnerabilities in the provided code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return category, response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error calling OpenAI API for {category}: {e}")
        return category, f"Error during analysis: {str(e)}"

async def analyze_code_section(code: str, categories: List[str]) -> List[AuditIssue]:
    """Analyze a section of code for security issues using OpenAI"""
    issues = []
    
    # Use entire contract text for analysis
    highlighted_code = code
    logging.info(f"Using entire contract text for analysis ({len(highlighted_code)} characters)")
    
    # Use the single auditor prompt for analysis
    prompt = auditor_prompt.format(code=code)
    analysis_tasks = [analyze_with_openai(prompt, "common")]
    
    # Run all analyses concurrently
    logging.info(f"Starting parallel analysis for {len(analysis_tasks)} vulnerability categories...")
    results = await asyncio.gather(*analysis_tasks)
    logging.info("Received all analyses from OpenAI")
    
    # Process results
    for category, analysis in results:
        issues.append(AuditIssue(
            category=category,
            description=analysis,
            severity="CRITICAL",
            code_context=highlighted_code
        ))
        logging.info(f"Created issue report for {category}")
    
    return issues

def generate_audit_tasks(contract_text: str) -> Generator[AuditTask, None, None]:
    """Generate a single audit task for the entire contract text"""
    yield AuditTask(
        category="common",
        template=auditor_prompt,
        code=contract_text,
        highlighted_section=contract_text,
        reference_id="entire_contract"
    )

async def get_audit_analysis(task: AuditTask, max_retries: int = 5) -> str:
    """Get initial vulnerability analysis with retries"""
    end_marker = "#END#"
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Format the template with the code
            prompt = task.template.format(code=task.code) + f"\n\nIMPORTANT: End your analysis with the marker {end_marker}"
            
            # Send to OpenAI for initial analysis
            response = await client.chat.completions.create(
                model=os.getenv("AI_MODEL"),
                messages=[
                    {"role": "system", "content": "You are an expert smart contract security auditor. Your task is to find critical vulnerabilities in the provided code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            
            # Check for end marker
            if not analysis.strip().endswith(end_marker):
                raise ValueError("Response does not end with the required marker")
                
            # Remove the end marker from the analysis
            final_analysis = analysis.strip()[:-len(end_marker)].strip()
            
            # Log the successful audit analysis request and response
            os.makedirs("logs", exist_ok=True)
            log_file = os.path.join("logs", f"{task.reference_id}_analysis.txt")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("Request prompt:\n")
                f.write(prompt)
                f.write("\n\nResponse:\n")
                f.write(final_analysis)
                f.write("\n\n-------------------\n")
                
            return final_analysis
            
        except Exception as e:
            last_error = e
            retry_delay = 2 ** attempt  # Exponential backoff
            logging.warning(f"Audit analysis failed for reference {task.reference_id}, category {task.category} (attempt {attempt + 1}/{max_retries}): {e}")
            logging.info(f"Retrying audit in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
            
    raise ValueError(f"Failed to get audit analysis after {max_retries} attempts: {last_error}")

async def get_critic_validation(code: str, analysis: str, task: AuditTask, max_retries: int = 5) -> Tuple[str, bool]:
    """Get critic's validation with retries"""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            prompt = critic_prompt.format(code=task.code, analysis=analysis)
            critic_response = await client.chat.completions.create(
                model=os.getenv("AI_MODEL"),
                messages=[
                    {"role": "system", "content": "You are an expert smart contract security auditor with years of experience in detecting false positives."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            
            critic_result = critic_response.choices[0].message.content.strip()
            
            # Check critic's verdict
            if not (critic_result.endswith('YES') or critic_result.endswith('NO')):
                raise ValueError("Critic's response does not end with YES or NO")
            
            # Log the successful critic validation request and response
            os.makedirs("logs", exist_ok=True)
            log_file = os.path.join("logs", f"{task.reference_id}_critic.txt")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("Critic Prompt:\n")
                f.write(prompt)
                f.write("\n\nCritic Response:\n")
                f.write(critic_result)
                f.write("\n\n-------------------\n")
                
            return critic_result, critic_result.endswith('YES')
            
        except Exception as e:
            last_error = e
            retry_delay = 2 ** attempt  # Exponential backoff
            logging.warning(f"Critic validation failed for reference {task.reference_id}, category {task.category} (attempt {attempt + 1}/{max_retries}): {e}")
            logging.info(f"Retrying critic in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
            
    raise ValueError(f"Failed to get critic validation after {max_retries} attempts: {last_error}")

async def process_audit_task(task: AuditTask, max_retries: int = 5) -> AuditIssue:
    """Process a single audit task with retries"""
    try:
        # Get initial analysis with retries
        logging.info(f"Getting audit analysis for reference {task.reference_id}, category {task.category}")
        analysis = await get_audit_analysis(task, max_retries)
        
        # Get critic validation with retries
        logging.info(f"Getting critic validation for reference {task.reference_id}, category {task.category}")
        critic_result, is_validated = await get_critic_validation(task.code, analysis, task, max_retries)
        
        return AuditIssue(
            category=task.category,
            description=f"VULNERABILITY ANALYSIS:\n{analysis}\n\nCRITIC'S VALIDATION:\n{critic_result}",
            severity="CRITICAL",
            code_context=task.highlighted_section,
            is_validated_by_critic=is_validated
        )
        
    except Exception as e:
        logging.error(f"Task processing failed for reference {task.reference_id}, category {task.category}: {e}")
        return AuditIssue(
            category=task.category,
            description=f"Error during analysis: {str(e)}",
            severity="ERROR",
            code_context=task.highlighted_section,
            is_validated_by_critic=False
        )

async def process_tasks_with_limit(tasks: Generator[AuditTask, None, None], max_concurrent: int) -> List[AuditIssue]:
    """Process tasks with concurrency limit"""
    semaphore = asyncio.Semaphore(max_concurrent)
    pending = set()
    completed_issues = []
    
    async def process_with_semaphore(task: AuditTask) -> AuditIssue:
        async with semaphore:
            logging.info(f"Processing reference {task.reference_id}, category {task.category}")
            return await process_audit_task(task)
    
    # Process tasks as they come from the generator
    for task in tasks:
        if len(pending) >= max_concurrent:
            # Wait for at least one task to complete
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            completed_issues.extend(t.result() for t in done)
        
        # Create and start new task
        coro = process_with_semaphore(task)
        pending.add(asyncio.create_task(coro))
    
    # Wait for remaining tasks
    if pending:
        done, _ = await asyncio.wait(pending)
        completed_issues.extend(t.result() for t in done)
    
    return completed_issues

async def audit_contract(file_path: str, max_concurrent_tasks: int = 16) -> List[AuditIssue]:
    """Audit a smart contract for security issues"""
    logging.info(f"Starting audit of {file_path}")
    
    # Read entire contract text
    logging.info("Reading smart contract text...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            contract_text = f.read()
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        sys.exit(1)
    logging.info(f"Read contract text ({len(contract_text)} characters)")

    # Generate and process a single audit task for the entire contract
    logging.info("Generating audit task for entire contract...")
    tasks = generate_audit_tasks(contract_text)
    issues = await process_tasks_with_limit(tasks, max_concurrent_tasks)
    
    # Filter out error issues
    valid_issues = [issue for issue in issues if issue.severity != "ERROR"]
    
    logging.info(f"Audit complete. Found {len(valid_issues)} potential issues.")
    return valid_issues

async def main_async():
    if len(sys.argv) != 2:
        print("Usage: python simple-agent.py <solidity_file>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    if not Path(file_path).exists():
        print(f"File not found: {file_path}")
        sys.exit(1)
    
    logging.info("Starting smart contract security audit")
    logging.info("=====================================")
        
    issues = await audit_contract(file_path)
    
    # Print findings
    if not issues:
        logging.info("No critical or major issues found.")
        return
    
    # Sort issues by critic validation (validated first)
    issues.sort(key=lambda x: not x.is_validated_by_critic)  # not to reverse order
    
    # Count validated issues
    validated_count = sum(1 for issue in issues if issue.is_validated_by_critic)
        
    print("\nAudit Summary:")
    print("=============")
    print(f"Total issues found: {len(issues)}")
    print(f"Issues confirmed by critic: {validated_count}")
    print(f"Issues rejected by critic: {len(issues) - validated_count}")
    
    print("\nDetailed Findings:")
    print("=================")
    
    # Print validated issues first
    if validated_count > 0:
        print("\n🔴 CONFIRMED VULNERABILITIES:")
        print("---------------------------")
        for i, issue in enumerate((i for i in issues if i.is_validated_by_critic), 1):
            print(f"\nIssue #{i} (Critic: ✓ Confirmed)")
            print(f"Category: {issue.category}")
            print(f"Severity: {issue.severity}")
            print(f"Description: {issue.description}")
            print("\nRelevant Code:")
            print("--------------")
            print(issue.code_context)
            print("--------------")
    
    # Then print rejected issues
    if len(issues) - validated_count > 0:
        print("\n⚠️  REJECTED FINDINGS:")
        print("-------------------")
        for i, issue in enumerate((i for i in issues if not i.is_validated_by_critic), 1):
            print(f"\nIssue #{i} (Critic: ✗ Rejected)")
            print(f"Category: {issue.category}")
            print(f"Severity: {issue.severity}")
            print(f"Description: {issue.description}")
            print("\nRelevant Code:")
            print("--------------")
            print(issue.code_context)
            print("--------------")
    
    logging.info("Audit report generated successfully")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main() 
