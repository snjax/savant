import sys
import os
import re
from pathlib import Path


from haystack import Pipeline
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentCleaner
# from haystack.components.preprocessors import DocumentSplitter
from haystack.components.joiners import DocumentJoiner
from haystack.components.routers import FileTypeRouter
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.utils import Secret
from haystack.components.converters import TextFileToDocument
from haystack.components.joiners import DocumentJoiner


# LLM Configuration with environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "test")
# Use default OpenAI API URL if a real API key is provided, otherwise use the local URL
OPENAI_URL = None if OPENAI_API_KEY != "test" else os.getenv("OPENAI_API_BASE_URL", "http://127.0.0.1:1234/v1")
OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "1000000"))


template = """
Extract only the issues that are marked or described as critical, major or high severity issues from the document.
Ignore every other type of issue (e.g. minor, low and medium).
Ways to obtain the file URL:
    1. If the URL is included in the issue directly, use it.
    2. If only the file path/name is specified in the issue, combine the global project/commit url with the file path/name specified in the issue.
    3. If only the contract name is specified in the issue, combine the global project/commit url with the contract name specified in the issue (e.g. [commit url] + "/contracts/[contract_name].sol").

Line numbers are optional. Use them if they are specified in the issue, leave empty otherwise. Line numers format: 0-123 for range, 123 for single line. 0-123,123 for multiple ranges.

Analyze the document step by step:
1. Extract the url of the repository from the document. Only use the unfixed commit URL.
2. Make a list of all issues using the following format: "Issue Title" | "Issue Severity" | "File name" | "Line Numbers"
3. Make a list of issues between "<<<<< ISSUE"S" and ">>>>> ISSUES" in the following markdown format:

<<<<<<< ISSUES
## [Issue title]
### Severity
[Issue Severity]
### File URL
[File URL]
### Line Numbers
[Line Numbers]
### Description
[Description]
>>>>>>> ISSUES

Document:
{{ document }}
"""

def check_directory_for_errors(file_path):
    prep_pipeline = Pipeline()
    prep_pipeline.add_component("file_type_router", FileTypeRouter(mime_types=["application/pdf", "text/markdown"]))
    prep_pipeline.add_component("pypdf_converter", PyPDFToDocument())
    prep_pipeline.add_component("markdown_converter", TextFileToDocument())
    prep_pipeline.add_component("cleaner", DocumentCleaner())
    # prep_pipeline.add_component("splitter", DocumentSplitter(split_by="word", split_length=8192, split_overlap=100, split_threshold=1024)) # FIXME
    prep_pipeline.add_component("joiner", DocumentJoiner())
    prep_pipeline.connect("file_type_router.application/pdf", "pypdf_converter.sources")
    prep_pipeline.connect("file_type_router.text/markdown", "markdown_converter.sources")
    prep_pipeline.connect("pypdf_converter", "joiner")
    prep_pipeline.connect("markdown_converter", "joiner")
    prep_pipeline.connect("joiner", "cleaner")
    # prep_pipeline.connect("cleaner", "splitter")

    docs = prep_pipeline.run({
        "file_type_router": {"sources": [Path(file_path)]},
    })["cleaner"]["documents"]

    llm_pipeline = Pipeline()
    llm_pipeline.add_component("llm", OpenAIGenerator(
        **({"api_base_url": OPENAI_URL} if OPENAI_URL else {}),
        api_key=Secret.from_token(OPENAI_API_KEY),
        timeout=OPENAI_TIMEOUT
    ))
    llm_pipeline.add_component("prompt_builder", PromptBuilder(template=template))
    llm_pipeline.connect("prompt_builder", "llm")

    # TODO: Is there a better way to do multiple documents/queries at once?
    results = []
    for doc in docs:
        result = llm_pipeline.run({
            "prompt_builder": {"document": doc.content},
        })["llm"]["replies"][0]

        issues = re.findall(r"<<<<<<< ISSUES\n(.*)\n>>>>>>> ISSUES", result, re.DOTALL)
        res = issues[-1]

        results.append(res)

    return "\n".join(results)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file> [output_file]")
        sys.exit(1)

    file_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else './issues.md'
    
    issues = check_directory_for_errors(file_path)

    title = file_path.split('/')[-1]
    issues = f"\n# {title}\n\n{issues}"

    with open(output_file, 'a') as f:
        f.write(issues)

    print(issues)
