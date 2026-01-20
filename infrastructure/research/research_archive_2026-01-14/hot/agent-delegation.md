---
topic: "agent-delegation"
category: "gemini"
tier: "hot"
tags:
  - "delegation"
  - "agents"
  - "multi-agent"
  - "prompts"
created: "2026-01-11 02:24 PM"
last_accessed: "2026-01-11 03:31 PM"
access_count: 2
---

## Related Research

- **agent-memory.md** - Session handoff and state persistence
- **agent-system-structure.md** - Agent registries and routing
- **agent-instruction-design.md** - Writing delegation prompts that work

---

## 2026-01-11 02:24 PM | Session: ProtocolTest

Excellent question. Here are some best practices for delegation in multi-agent AI systems, broken down by the areas you specified.

### 1. How to Structure Delegation Prompts

The key to a good delegation prompt is to be clear, concise, and unambiguous. The goal is to create a prompt that functions like a well-defined API call.

*   **Role-Based Instructions:** Start by defining the role of the agent you're delegating to. This puts the agent in the correct "mindset." For example: `You are a senior software engineer specializing in Python.`
*   **Clear, Actionable Objective:** State the primary goal of the task. Use action verbs. For example: `Refactor the 'user_auth.py' module to use the 'AuthService' class.`
*   **Provide Essential Context:** Include critical information the agent *must* have to start. This includes file paths, relevant code snippets, or user requirements.
*   **Define Constraints and Rules:** Specify any rules, conventions, or limitations. For example: `Do not add any new library dependencies.` or `Ensure all new code adheres to the existing style (PEP 8).`
*   **Specify Output Format:** Clearly state what the expected output should be. This is crucial for parsing the result. For example: `Return a JSON object with two keys: 'success' (boolean) and 'filePath' (string).` or `Provide only the updated Python code for the 'user_auth.py' file.`

**Example Prompt Structure:**

```
You are a <ROLE>.

Your objective is to <ACTIONABLE GOAL>.

**Context:**
- The primary file to modify is: `<FILE_PATH>`
- Here is the relevant configuration: `<CONFIG_SNIPPET>`

**Rules:**
- <RULE_1>
- <RULE_2>

**Output:**
- Respond with <EXPECTED_OUTPUT_FORMAT>.
```

### 2. Information to Pass vs. Let Agents Discover

Deciding what information to provide upfront versus what to let an agent discover is a trade-off between prompt efficiency and execution reliability.

*   **Pass Critical Information:** Always pass information that is absolutely essential for the task and difficult or impossible for the agent to discover on its own. This includes:
    *   The user's specific intent or goal.
    *   Relevant file paths you've already identified.
    *   Specific error messages or outputs that triggered the delegation.
    *   Any secrets or credentials required (handled securely, of course).

*   **Let Agents Discover Stable, General Information:** Let the agent discover information that is part of the general project context and is unlikely to be ambiguous. This empowers the agent to work more autonomously and reduces the initial prompt size. Examples include:
    *   Project structure (`ls -R`).
    *   Code style conventions (by reading existing files).
    *   Available libraries (`package.json`, `requirements.txt`).
    *   How to run tests (by finding a `README.md` or a testing configuration file).

**A good heuristic:** If the information is *static and universal* to the project, let the agent find it. If the information is *dynamic and specific* to the immediate task, pass it directly.

### 3. How to Handle Results from Child Agents

The parent agent must be able to reliably parse and act on the child agent's output.

*   **Strictly Enforce Output Format:** The most important practice is to demand a predictable output format (as mentioned in point 1). JSON is often the best choice because it's structured, machine-readable, and supported by virtually all programming languages.
*   **Validate the Output:** Before using the result, validate it against the expected schema. Did the agent return the right keys? Are the data types correct?
*   **Implement Error Handling:** Have a clear plan for when a sub-agent fails. The sub-agent's response should include a clear success/failure flag. If it fails, it should provide a concise error message that the parent agent can use to debug or retry the task.
*   **Integrate and Verify:** Once a successful result is received and validated, the parent agent integrates it into its plan. For a code change, this might mean writing the code to a file and then running the project's test suite to verify that the change works as expected and didn't introduce any regressions.

### 4. Patterns for Minimal-Token Returns

Minimizing token usage is critical for efficiency and reducing costs.

*   **Structured Data (JSON):** Instead of returning natural language, have the agent return compact JSON.
    *   **Bad (Verbose):** `"I have successfully refactored the file. The updated file is located at 'src/auth/service.py'. I did not encounter any errors."`
    *   **Good (Minimal):** `{"success": true, "filePath": "src/auth/service.py", "error": null}`
*   **Use Booleans and Enums:** Use boolean flags (`true`/`false`) and enumerated types (`"status": "COMPLETED"`) instead of descriptive strings.
*   **Return Pointers, Not Content:** If a child agent modifies a large file, it should not return the entire file's content. Instead, it should save the file itself and return the path to the file. The parent agent can then decide if it needs to read the file.
*   **Summarization and Confirmation:** For tasks involving analysis or discovery, have the child agent return a concise summary or just a confirmation.
    *   **Task:** `"Analyze the 'package.json' and determine if 'axios' is a dependency."`
    *   **Bad Return:** The entire content of `package.json`.
    *   **Good Return:** `{"dependencyFound": true, "version": "^1.6.0"}`
