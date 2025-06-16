# Codex User Guide

## Introduction

Codex is an AI-powered coding assistant integrated with the Tekton platform. Based on Aider, Codex provides an intelligent pair programming experience that helps you write, modify, and optimize code across 100+ programming languages.

This guide will help you get started with Codex and leverage its capabilities within the Tekton environment.

## Getting Started

### Launching Codex

There are several ways to launch Codex as part of your Tekton environment:

1. **Using the Aider flag**:
   ```bash
   ./launch-tekton.sh --aider
   ```

2. **As part of the full stack**:
   ```bash
   ./launch-tekton.sh --full-stack
   ```

3. **Specifying components manually**:
   ```bash
   ./launch-tekton.sh --components engram,hermes,hephaestus,codex
   ```

### Accessing the Codex UI

Once Tekton is running with Codex enabled:

1. Open the Tekton UI in your browser (typically at http://localhost:8080)
2. Select "Codex" from the left sidebar component list
3. Codex will appear in the RIGHT PANEL of the Tekton interface
4. The chat input in the RIGHT FOOTER will be used for communicating with Codex

## Using Codex

### UI Layout

The Codex interface consists of three main panels that you can switch between:

1. **Console Panel** (default): Shows the conversation with Aider and its outputs
2. **Files Panel**: Displays a list of files that are currently in context
3. **Settings Panel**: Provides quick commands and usage tips

### Starting a Session

When you first access Codex, a session will automatically start. If needed, you can manually start a new session:

1. Click the "New Session" button in the Codex header
2. Wait for the session to initialize (indicated by the status changing to "Active")
3. Once active, you can begin interacting with Aider through the chat input

### Basic Interaction

To interact with Codex:

1. Type your questions or instructions in the chat input box in the RIGHT FOOTER
2. Press Enter to send your message to Aider
3. Aider will process your request and respond in the Console panel
4. Code blocks in the response will be properly formatted for readability

### File Operations

Codex can work with files in your codebase. Here are common file operations:

1. **Adding files to the conversation**:
   ```
   /add path/to/your/file.py
   ```

2. **Focusing on a specific file**:
   ```
   /focus path/to/your/file.py
   ```

3. **Viewing active files**:
   - Check the Files panel to see which files are currently in context
   - Click on a file in the Files panel to focus on it

4. **Listing directory contents**:
   ```
   /ls [optional/path]
   ```

### Code Editing Capabilities

Codex can help you with various coding tasks:

1. **Creating new files**:
   ```
   Can you create a new file called app.py with a basic Flask web server?
   ```

2. **Modifying existing code**:
   ```
   Please add error handling to the database connection function in db_utils.py
   ```

3. **Fixing bugs**:
   ```
   The pagination in list_view.js isn't working correctly. Can you help me fix it?
   ```

4. **Implementing features**:
   ```
   I need to implement JWT authentication in my Express app. Can you help?
   ```

5. **Refactoring code**:
   ```
   Can you refactor the User class in models.py to use composition instead of inheritance?
   ```

### Git Integration

Codex includes built-in Git integration:

1. **Viewing Git status**:
   ```
   /git
   ```

2. **Committing changes**:
   ```
   /commit
   ```
   or
   ```
   /commit Your commit message here
   ```

3. **Git operations**:
   ```
   /git [any git command]
   ```

### Advanced Commands

Codex supports various commands to enhance your workflow:

1. **Getting help**:
   ```
   /help
   ```

2. **Limiting context to specific files**:
   ```
   /drop
   /add only/files/you/need.py
   ```

3. **Running shell commands**:
   ```
   !ls -la
   ```
   or
   ```
   /run ls -la
   ```

4. **Using voice input** (if supported by your browser):
   ```
   /voice
   ```

5. **Exiting the Aider session**:
   ```
   /exit
   ```

## Best Practices

### Effective Communication

For best results with Codex:

1. **Be specific**: Clearly describe what you want to accomplish
   ```
   # Good example
   Can you add input validation to the registerUser function in auth.js to check that emails are valid and passwords are at least 8 characters?
   
   # Less effective example
   Fix the user registration
   ```

2. **Provide context**: Include information about your project and requirements
   ```
   I'm building a React app with TypeScript. Can you help me create a custom hook that fetches data and handles loading/error states?
   ```

3. **Break down complex tasks**: Ask for one thing at a time for complex changes
   ```
   First, let's set up the database schema. Then we'll work on the API endpoints.
   ```

### Working with Larger Codebases

For efficient work in larger projects:

1. **Use Repomap**: Aider automatically creates a map of your codebase to understand relationships
   ```
   /map
   ```

2. **Focus on relevant files**: Don't add more files than necessary to the conversation
   ```
   /add only/the/files/needed.js
   ```

3. **Use incremental changes**: Build up complex features step by step

### Troubleshooting

If you encounter issues:

1. **Session not starting**: Try clicking the "New Session" button or refreshing the page

2. **Connection issues**: Check if the Codex server is running with:
   ```bash
   ps aux | grep codex_server
   ```

3. **Input not being processed**: Make sure the session status shows as "Active"

4. **Unexpected behavior**: Try restarting the session with the "New Session" button

## Examples

### Example 1: Creating a Simple Web Server

```
Can you help me create a simple web server in Python using Flask? 
I need it to have a home page and an API endpoint that returns JSON data.
```

### Example 2: Debugging Existing Code

```
I have an issue with my sorting function in utils.js. When I sort an array with duplicate values, it's not stable. Here's the current implementation:

function customSort(array, key) {
    return array.sort((a, b) => a[key] - b[key]);
}

Can you identify the issue and fix it?
```

### Example 3: Implementing a Feature

```
I need to implement a caching system for my API responses in my Express app. 
Can you help me add Redis caching with a 5-minute expiration time for the getProducts endpoint in routes/products.js?
```

### Example 4: Code Refactoring

```
The UserService class in user_service.py has grown too large. 
Can you help me refactor it using the Single Responsibility Principle to split it into smaller, more focused classes?
```

## Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Display help information | `/help` |
| `/add` | Add file(s) to the chat | `/add src/app.js` |
| `/focus` | Focus on a specific file | `/focus src/app.js` |
| `/drop` | Remove file(s) from the chat | `/drop src/app.js` or `/drop` (all) |
| `/ls` | List directory contents | `/ls src` |
| `/git` | Run git commands | `/git status` |
| `/commit` | Commit changes | `/commit Fix login bug` |
| `/map` | Show or create a repo map | `/map` |
| `/run` | Run a shell command | `/run npm test` |
| `!` | Shorthand for /run | `!ls -la` |
| `/diff` | Show diffs of files | `/diff` or `/diff src/app.js` |
| `/voice` | Toggle voice input mode | `/voice` |
| `/exit` | Exit the Aider session | `/exit` |

## Conclusion

Codex brings the power of AI pair programming to your Tekton environment, helping you code more effectively and efficiently. With its natural language interface and understanding of your codebase, Codex serves as an intelligent coding assistant that can help with everything from simple tasks to complex features.

For more detailed information, refer to the [Aider documentation](https://aider.chat/docs/) and explore the various commands and capabilities as you use Codex in your daily development workflow.