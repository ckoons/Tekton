
# Codex

<div align="center">
  <img src="images/icon.jpg" alt="Codex Logo" width="800"/>
  <h3>Codex<br>AI Design & Coding Platform</h3>
</div>

> AI-powered design and coding platform

## Overview

Codex is a next-generation design and coding platform, based on Aider, that uses artificial intelligence to help engineers, designers, and makers create optimized products. By combining advanced AI programming capabilities with a seamless user interface, Codex transforms how software is designed, implemented, and maintained.

## Tekton Integration

Codex has been integrated with the Tekton platform as a specialized coding component. This integration provides:

1. A unified UI experience with Codex available in the Tekton RIGHT PANEL
2. Input handling through the Tekton chat interface in the RIGHT FOOTER
3. Seamless context sharing with other Tekton components
4. Registration with Hermes for component discovery

### Using Codex with Tekton

To use Codex with Tekton:

1. Start Tekton with the Codex component: `./launch-tekton.sh --components engram,hermes,codex`
2. Select the "Codex" component from the left sidebar in the Tekton UI
3. Interact with Aider through the chat interface

For more details, see the [adapter README](adapter/README.md)

## Key Features

<p align="center">
<!--[[[cog
from scripts.badges import get_badges_md
text = get_badges_md()
cog.out(text)
]]]-->
  <a href="https://github.com/Aider-AI/aider/stargazers"><img alt="GitHub Stars" title="Total number of GitHub stars the Aider project has received"
src="https://img.shields.io/github/stars/Aider-AI/aider?style=flat-square&logo=github&color=f1c40f&labelColor=555555"/></a>
  <a href="https://pypi.org/project/aider-chat/"><img alt="PyPI Downloads" title="Total number of installations via pip from PyPI"
src="https://img.shields.io/badge/📦%20Installs-1.7M-2ecc71?style=flat-square&labelColor=555555"/></a>
  <img alt="Tokens per week" title="Number of tokens processed weekly by Aider users"
src="https://img.shields.io/badge/📈%20Tokens%2Fweek-15B-3498db?style=flat-square&labelColor=555555"/>
  <a href="https://openrouter.ai/"><img alt="OpenRouter Ranking" title="Aider's ranking among applications on the OpenRouter platform"
src="https://img.shields.io/badge/🏆%20OpenRouter-Top%2020-9b59b6?style=flat-square&labelColor=555555"/></a>
  <a href="https://aider.chat/HISTORY.html"><img alt="Singularity" title="Percentage of the new code in Aider's last release written by Aider itself"
src="https://img.shields.io/badge/🔄%20Singularity-65%25-e74c3c?style=flat-square&labelColor=555555"/></a>
<!--[[[end]]]-->  
</p>

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

Check out our [Examples Gallery](https://forge.ai/examples) to see what you can build with Codex:

- Mechanical components with optimized weight-to-strength ratios
- Fluid dynamics-optimized designs
- Generative furniture designs
- Custom prosthetics and medical devices
- Architectural elements and components

## Contributing

We welcome contributions to Codex! See our [Contributing Guide](CONTRIBUTING.md) for details on:

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

Codex is available under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

- This project uses the Claude API for AI capabilities
- CAD core based on OpenCascade
- Optimization engine powered by TensorFlow and PyTorch
- Rendering engine based on three.js

---

<p align="center">Made with ❤️ by the Codex team</p>

<p align="center">
    <a href="https://aider.chat/"><img src="https://aider.chat/assets/logo.svg" alt="Aider Logo" width="300"></a>
</p>

<h1 align="center">
AI Pair Programming in Your Terminal
</h1>


<p align="center">
Aider lets you pair program with LLMs to start a new project or build on your existing codebase. 
</p>

<p align="center">
  <img
    src="https://aider.chat/assets/screencast.svg"
    alt="aider screencast"
  >
</p>

<p align="center">
<!--[[[cog
from scripts.badges import get_badges_md
text = get_badges_md()
cog.out(text)
]]]-->
  <a href="https://github.com/Aider-AI/aider/stargazers"><img alt="GitHub Stars" title="Total number of GitHub stars the Aider project has received"
src="https://img.shields.io/github/stars/Aider-AI/aider?style=flat-square&logo=github&color=f1c40f&labelColor=555555"/></a>
  <a href="https://pypi.org/project/aider-chat/"><img alt="PyPI Downloads" title="Total number of installations via pip from PyPI"
src="https://img.shields.io/badge/📦%20Installs-1.7M-2ecc71?style=flat-square&labelColor=555555"/></a>
  <img alt="Tokens per week" title="Number of tokens processed weekly by Aider users"
src="https://img.shields.io/badge/📈%20Tokens%2Fweek-15B-3498db?style=flat-square&labelColor=555555"/>
  <a href="https://openrouter.ai/"><img alt="OpenRouter Ranking" title="Aider's ranking among applications on the OpenRouter platform"
src="https://img.shields.io/badge/🏆%20OpenRouter-Top%2020-9b59b6?style=flat-square&labelColor=555555"/></a>
  <a href="https://aider.chat/HISTORY.html"><img alt="Singularity" title="Percentage of the new code in Aider's last release written by Aider itself"
src="https://img.shields.io/badge/🔄%20Singularity-92%25-e74c3c?style=flat-square&labelColor=555555"/></a>
<!--[[[end]]]-->  
</p>

## Features

- 🧠 **[Cloud and local LLMs](https://aider.chat/docs/llms.html)** - Aider works best with Claude 3.7 Sonnet, DeepSeek R1 & Chat V3, OpenAI o1, o3-mini & GPT-4o, but can connect to almost any LLM, including local models.
- 🗺️ **[Maps your codebase](https://aider.chat/docs/repomap.html)** - Aider makes a map of your entire codebase, which helps it work well in larger projects.
- `</>` **[100+ code languages](https://aider.chat/docs/languages.html)** - Aider works with most popular programming languages: python, javascript, rust, ruby, go, cpp, php, html, css, and dozens more.
- 🔀 **[Git integration](https://aider.chat/docs/git.html)** - Aider automatically commits changes with sensible commit messages. Use familiar git tools to easily diff, manage and undo AI changes.
- 🖥️ **[Use in your IDE](https://aider.chat/docs/usage/watch.html)** - Use aider from within your favorite IDE or editor. Ask for changes by adding comments to your code and aider will get to work.
- 🖼️ **[Images & web pages](https://aider.chat/docs/usage/images-urls.html)** - Add images and web pages to the chat to provide visual context, screenshots, reference docs, etc.
- 🎤 **[Voice-to-code](https://aider.chat/docs/usage/voice.html)** - Speak with aider about your code! Request new features, test cases or bug fixes using your voice and let aider implement the changes.
- ✅ **[Linting & testing](https://aider.chat/docs/usage/lint-test.html)** - Automatically lint and test your code every time aider makes changes. Aider can fix problems detected by your linters and test suites.
- 📋 **[Copy/paste to web chat](https://aider.chat/docs/usage/copypaste.html)** - Work with any LLM via its web chat interface. Aider streamlines copy/pasting code context and edits back and forth with a browser.

## Getting Started

```bash
python -m pip install aider-install
aider-install

# Change directory into your codebase
cd /to/your/project

# DeepSeek
aider --model deepseek --api-key deepseek=<key>

# Claude 3.7 Sonnet
aider --model sonnet --api-key anthropic=<key>

# o3-mini
aider --model o3-mini --api-key openai=<key>
```

See the [installation instructions](https://aider.chat/docs/install.html) and [usage documentation](https://aider.chat/docs/usage.html) for more details.

## More Information

### Documentation
- [Installation Guide](https://aider.chat/docs/install.html)
- [Usage Guide](https://aider.chat/docs/usage.html)
- [Tutorial Videos](https://aider.chat/docs/usage/tutorials.html)
- [Connecting to LLMs](https://aider.chat/docs/llms.html)
- [Configuration Options](https://aider.chat/docs/config.html)
- [Troubleshooting](https://aider.chat/docs/troubleshooting.html)
- [FAQ](https://aider.chat/docs/faq.html)

### Community & Resources
- [LLM Leaderboards](https://aider.chat/docs/leaderboards/)
- [GitHub Repository](https://github.com/Aider-AI/aider)
- [Discord Community](https://discord.gg/Tv2uQnR88V)
- [Blog](https://aider.chat/blog/)

## Kind Words From Users

- *"The best free open source AI coding assistant."* — [IndyDevDan](https://youtu.be/YALpX8oOn78)
- *"The best AI coding assistant so far."* — [Matthew Berman](https://www.youtube.com/watch?v=df8afeb1FY8)
- *"Aider ... has easily quadrupled my coding productivity."* — [SOLAR_FIELDS](https://news.ycombinator.com/item?id=36212100)
- *"It's a cool workflow... Aider's ergonomics are perfect for me."* — [qup](https://news.ycombinator.com/item?id=38185326)
- *"It's really like having your senior developer live right in your Git repo - truly amazing!"* — [rappster](https://github.com/Aider-AI/aider/issues/124)
- *"What an amazing tool. It's incredible."* — [valyagolev](https://github.com/Aider-AI/aider/issues/6#issue-1722897858)
- *"Aider is such an astounding thing!"* — [cgrothaus](https://github.com/Aider-AI/aider/issues/82#issuecomment-1631876700)
- *"It was WAY faster than I would be getting off the ground and making the first few working versions."* — [Daniel Feldman](https://twitter.com/d_feldman/status/1662295077387923456)
- *"THANK YOU for Aider! It really feels like a glimpse into the future of coding."* — [derwiki](https://news.ycombinator.com/item?id=38205643)
- *"It's just amazing. It is freeing me to do things I felt were out my comfort zone before."* — [Dougie](https://discord.com/channels/1131200896827654144/1174002618058678323/1174084556257775656)
- *"This project is stellar."* — [funkytaco](https://github.com/Aider-AI/aider/issues/112#issuecomment-1637429008)
- *"Amazing project, definitely the best AI coding assistant I've used."* — [joshuavial](https://github.com/Aider-AI/aider/issues/84)
- *"I absolutely love using Aider ... It makes software development feel so much lighter as an experience."* — [principalideal0](https://discord.com/channels/1131200896827654144/1133421607499595858/1229689636012691468)
- *"I have been recovering from multiple shoulder surgeries ... and have used aider extensively. It has allowed me to continue productivity."* — [codeninja](https://www.reddit.com/r/OpenAI/s/nmNwkHy1zG)
- *"I am an aider addict. I'm getting so much more work done, but in less time."* — [dandandan](https://discord.com/channels/1131200896827654144/1131200896827654149/1135913253483069470)
- *"After wasting $100 on tokens trying to find something better, I'm back to Aider. It blows everything else out of the water hands down, there's no competition whatsoever."* — [SystemSculpt](https://discord.com/channels/1131200896827654144/1131200896827654149/1178736602797846548)
- *"Aider is amazing, coupled with Sonnet 3.5 it's quite mind blowing."* — [Josh Dingus](https://discord.com/channels/1131200896827654144/1133060684540813372/1262374225298198548)
- *"Hands down, this is the best AI coding assistant tool so far."* — [IndyDevDan](https://www.youtube.com/watch?v=MPYFPvxfGZs)
- *"[Aider] changed my daily coding workflows. It's mind-blowing how a single Python application can change your life."* — [maledorak](https://discord.com/channels/1131200896827654144/1131200896827654149/1258453375620747264)
- *"Best agent for actual dev work in existing codebases."* — [Nick Dobos](https://twitter.com/NickADobos/status/1690408967963652097?s=20)
