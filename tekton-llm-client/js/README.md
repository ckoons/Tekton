# Tekton LLM Client for Browser

A unified client for interacting with Tekton LLM services in the browser.

## Installation

```bash
npm install tekton-llm-client
```

## Usage

### Basic Text Generation

```javascript
// Initialize the client
const client = new TektonLLMClient({
  componentId: 'my-component',
  rhetorUrl: '/api/llm'  // URL to your Rhetor API endpoint
});

// Generate text
async function generateText() {
  try {
    const response = await client.generateText(
      "What is the capital of France?", 
      {
        systemPrompt: "You are a helpful assistant that provides accurate information.",
        temperature: 0.7
      }
    );
    
    console.log(response.content);
  } catch (error) {
    console.error("Error generating text:", error);
  }
}
```

### Chat Conversation

```javascript
// Generate a chat response
async function chatConversation() {
  const messages = [
    { role: "system", content: "You are a helpful assistant." },
    { role: "user", content: "Hello, how are you?" },
    { role: "assistant", content: "I'm doing well, thanks for asking! How can I help you today?" },
    { role: "user", content: "What's the weather like in Paris today?" }
  ];
  
  try {
    const response = await client.generateChatResponse(messages);
    console.log(response.content);
  } catch (error) {
    console.error("Error in chat:", error);
  }
}
```

### Streaming

```javascript
// Stream a response
function streamResponse() {
  let fullResponse = "";
  
  const requestId = client.streamText(
    "Write a short poem about AI.", 
    (chunk) => {
      // Process each chunk as it arrives
      fullResponse += chunk.chunk;
      console.log("Received chunk:", chunk.chunk);
      
      if (chunk.done) {
        console.log("Full response:", fullResponse);
      }
    },
    {
      onComplete: () => console.log("Streaming completed"),
      onError: (error) => console.error("Streaming error:", error)
    }
  );
  
  // You can cancel the stream if needed
  // setTimeout(() => client.cancelRequest(requestId), 5000);
}
```

### Provider Information

```javascript
// Get available providers and models
async function getProviders() {
  try {
    const providersInfo = await client.getProviders();
    console.log("Available providers:", providersInfo);
  } catch (error) {
    console.error("Error fetching providers:", error);
  }
}
```

## API Reference

### TektonLLMClient

```typescript
constructor(options: {
  componentId: string;
  rhetorUrl?: string;
  rhetorWsUrl?: string;
  providerId?: string;
  modelId?: string;
  timeout?: number;
  authToken?: string;
  debug?: boolean;
})
```

#### Methods

- `generateText(prompt: string, options?: GenerationOptions): Promise<CompletionResponse>`
- `generateChatResponse(messages: ChatMessage[], options?: GenerationOptions): Promise<CompletionResponse>`
- `streamText(prompt: string, onChunk: (chunk: StreamingChunk) => void, options?: StreamingOptions): string`
- `streamChatResponse(messages: ChatMessage[], onChunk: (chunk: StreamingChunk) => void, options?: StreamingOptions): string`
- `cancelRequest(requestId: string): boolean`
- `getProviders(): Promise<ProvidersResponse>`

## License

MIT