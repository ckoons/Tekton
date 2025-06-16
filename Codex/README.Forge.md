# Forge

<div align="center">
  <img src="images/icon.jpg" alt="Forge Logo" width="800"/>
  <h3>Forge<br>AI Design & Coding Platform</h3>
</div>
`
> AI-powered design and coding platform

## Overview

Forge is a next-generation design and coding platform, based on Aider, that uses artificial intelligence to help engineers, designers, and makers create optimized physical products. By combining advanced CAD/CAM capabilities with AI assistance, Forge transforms how products are designed, tested, and manufactured.

## Key Features

### Intelligent Design Assistant

- Natural language interface for creating and modifying designs
- Real-time design guidance and recommendations
- Automatic generation of design alternatives
- Design validation against manufacturing constraints

<<<<<<< HEAD
### Advanced Optimization

- Multi-parameter optimization for performance, cost, and manufacturability
- Topology optimization based on load conditions and material properties
- Weight reduction while maintaining structural integrity
- Material selection optimization based on requirements

### Manufacturing Integration

- Automatic generation of manufacturing instructions
- Support for CNC machining, 3D printing, laser cutting, and more
- Cost estimation and manufacturing time prediction
- Direct connection to manufacturing service providers

### Collaboration Tools

- Real-time collaborative design environment
- Version control and design history
- Commenting and feedback systems
- Team permissions and access control
=======
### [Cloud and local LLMs](https://aider.chat/docs/llms.html)

<a href="https://aider.chat/docs/llms.html"><img src="https://aider.chat/assets/icons/brain.svg" width="32" height="32" align="left" valign="middle" style="margin-right:10px"></a>
Aider works best with Claude 3.7 Sonnet, DeepSeek R1 & Chat V3, OpenAI o1, o3-mini & GPT-4o, but can connect to almost any LLM, including local models.

<br>

### [Maps your codebase](https://aider.chat/docs/repomap.html)

<a href="https://aider.chat/docs/repomap.html"><img src="https://aider.chat/assets/icons/map-outline.svg" width="32" height="32" align="left" valign="middle" style="margin-right:10px"></a>
Aider makes a map of your entire codebase, which helps it work well in larger projects.

<br>

### [100+ code languages](https://aider.chat/docs/languages.html)

<a href="https://aider.chat/docs/languages.html"><img src="https://aider.chat/assets/icons/code-tags.svg" width="32" height="32" align="left" valign="middle" style="margin-right:10px"></a>
Aider works with most popular programming languages: python, javascript, rust, ruby, go, cpp, php, html, css, and dozens more.

<br>

### [Git integration](https://aider.chat/docs/git.html)

<a href="https://aider.chat/docs/git.html"><img src="https://aider.chat/assets/icons/source-branch.svg" width="32" height="32" align="left" valign="middle" style="margin-right:10px"></a>
Aider automatically commits changes with sensible commit messages. Use familiar git tools to easily diff, manage and undo AI changes.

<br>

### [Use in your IDE](https://aider.chat/docs/usage/watch.html)

<a href="https://aider.chat/docs/usage/watch.html"><img src="https://aider.chat/assets/icons/monitor.svg" width="32" height="32" align="left" valign="middle" style="margin-right:10px"></a>
Use aider from within your favorite IDE or editor. Ask for changes by adding comments to your code and aider will get to work.

<br>

### [Images & web pages](https://aider.chat/docs/usage/images-urls.html)

<a href="https://aider.chat/docs/usage/images-urls.html"><img src="https://aider.chat/assets/icons/image-multiple.svg" width="32" height="32" align="left" valign="middle" style="margin-right:10px"></a>
Add images and web pages to the chat to provide visual context, screenshots, reference docs, etc.

<br>

### [Voice-to-code](https://aider.chat/docs/usage/voice.html)

<a href="https://aider.chat/docs/usage/voice.html"><img src="https://aider.chat/assets/icons/microphone.svg" width="32" height="32" align="left" valign="middle" style="margin-right:10px"></a>
Speak with aider about your code! Request new features, test cases or bug fixes using your voice and let aider implement the changes.

<br>

### [Linting & testing](https://aider.chat/docs/usage/lint-test.html)

<a href="https://aider.chat/docs/usage/lint-test.html"><img src="https://aider.chat/assets/icons/check-all.svg" width="32" height="32" align="left" valign="middle" style="margin-right:10px"></a>
Automatically lint and test your code every time aider makes changes. Aider can fix problems detected by your linters and test suites.

<br>

### [Copy/paste to web chat](https://aider.chat/docs/usage/copypaste.html)

<a href="https://aider.chat/docs/usage/copypaste.html"><img src="https://aider.chat/assets/icons/content-copy.svg" width="32" height="32" align="left" valign="middle" style="margin-right:10px"></a>
Work with any LLM via its web chat interface. Aider streamlines copy/pasting code context and edits back and forth with a browser.
>>>>>>> c7e8d297a470f02a685379a024faa817a5ba9c42

## Getting Started

### Prerequisites

- Node.js 20.x or higher
- Python 3.10 or higher
- Docker and Docker Compose
- GPU with CUDA support (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/forge.git
cd forge

# Install dependencies
npm install

# Set up the Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys and configuration

# Start the development environment
docker-compose up -d
```

### Quick Start

1. Launch the application: `npm start`
2. Open your browser to `http://localhost:3000`
3. Create a new project or open an example
4. Start designing with AI assistance

## Documentation

For detailed documentation, visit our [Documentation Portal](https://forge.ai/docs).

- [User Guide](https://forge.ai/docs/user-guide)
- [API Reference](https://forge.ai/docs/api)
- [Developer Guide](https://forge.ai/docs/developers)
- [Tutorials](https://forge.ai/docs/tutorials)

## Examples

Check out our [Examples Gallery](https://forge.ai/examples) to see what you can build with Forge:

- Mechanical components with optimized weight-to-strength ratios
- Fluid dynamics-optimized designs
- Generative furniture designs
- Custom prosthetics and medical devices
- Architectural elements and components

## Contributing

We welcome contributions to Forge! See our [Contributing Guide](CONTRIBUTING.md) for details on:

- Setting up your development environment
- Our coding standards and guidelines
- The pull request process
- Running tests and validation

## Community

- [Discord Community](https://discord.gg/forge-ai)
- [Forum](https://forum.forge.ai)
- [Twitter](https://twitter.com/forge_ai)
- [YouTube Channel](https://youtube.com/c/forge-ai)

## License

Forge is available under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

- This project uses the Claude API for AI capabilities
- CAD core based on OpenCascade
- Optimization engine powered by TensorFlow and PyTorch
- Rendering engine based on three.js

---

<p align="center">Made with ❤️ by the Forge team</p>
