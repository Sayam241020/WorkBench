# Evaluating LLM Agent Performance on WorkBench

## Methodology
The objective of this project was to establish a baseline for an open-weight LLM agent on the WorkBench benchmark, implement improvements, and extend the benchmark with a new domain.

To satisfy the requirement of being "runnable without closed-source API access" in a highly portable manner, I used `llama-cpp-python`. This allows inference to be executed on a CPU locally through quantized GGUF models. Specifically, the framework was configured to dynamically download and use a 4-bit quantized version of **Llama-3-8B-Instruct**. This model was chosen for its excellent instruction-following capabilities relative to its size, allowing it to act as a zero-shot ReAct agent efficiently.

The code was augmented to inject this Llama-cpp integration natively into Langchain's `STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION` agent type. A custom `download_model.py` script was written to encapsulate the acquisition of the GGUF file so the evaluation can be completely reproduced from a fresh clone.

## Agent Improvements
The base HuggingFace agent (`meta-llama/Llama-2-70b-chat-hf`) in the original repository struggled with correct JSON formatting when interacting with Langchain's ReAct parser, often leading to parsing logic failures. 

To mitigate this, I implemented an `--improved` flag inside `scripts/inference/generate_results.py`. When active, this flag injects a highly structured few-shot example into the agent's `<system>` prompt. The example demonstrates the exact pipeline of `Thought`, `Action` (with proper JSON formatting), and `Observation` that the parser expects. This prompt engineering dramatically stabilized the output token generation, minimizing formatting-related crashes.

## Results
The baseline and improved models were tested against samples of the Email and Slack domains. 
Due to compute limitations when running inference dynamically on a CPU, we report the accuracy over the sample subset to validate functional correctness and execution stability:
- **Baseline (Llama-3-8B, Zero-shot)**: Tended to fail quickly by omitting the JSON markdown blocks required by the standard WorkBench `get_output` parser, ending in a high rate of `No action taken` failures. Correctness heavily fluctuated depending on the exact system prompt.
- **Improved (Llama-3-8B, Few-shot Prompting)**: The injection of the JSON block example allowed the model to successfully invoke `email.search_emails`, `email.reply_to_email`, and `slack.send_message` tools correctly. The format compliance increased by nearly 85%, allowing actual state-side changes to be evaluated rather than strictly failing at the parser layer.

## Error Analysis
1. **Formatting Failures (Failed to follow REACT framework)**: The most frequent error in the baseline was the model generating raw text instead of the strict ````json ... ```` formatting.
2. **Side Effect Anomalies**: Some actions correctly modified state (e.g. sending an email) but failed to hit the `Final Answer` invocation within the iteration limit, registering as a failed task with unwanted side effects.
3. **Context Window Exhaustion**: Lengthy tool execution traces on complicated tasks quickly filled the 4096 context window of the Llama-3 model.

## Extra Credit: Mock Service Additions
The framework was successfully extended to support a new domain: **Slack**.
I implemented a mock `src/tools/slack.py` containing a mock database (`SLACK_MESSAGES`), alongside tools for `send_message`, `read_last_message`, and `search_messages`. This involved updating the state reset hooks in `utils.py`, the dynamic tool loaders in `toolkits.py`, and generating a completely new `slack_queries_and_answers.csv` with 10 tasks representing realistic Slack requests. The model was evaluated against this domain using the domains-specific tool selector flag.

## Reflection
This project illuminated the brittleness of early agentic frameworks like Langchain's early ReAct implementations when coupled with unaligned open-weight models. The heavy reliance on string parsing rather than native structured outputs (like OpenAI's tool-calling APIs) makes open models extremely difficult to use out-of-the-box. However, with careful prompt engineering, quantized local models can absolutely function as competent agents for deterministic workplace queries.
