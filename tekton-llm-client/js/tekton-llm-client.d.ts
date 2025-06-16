/**
 * TypeScript definitions for Tekton LLM Client.
 */

/**
 * Message in a chat conversation.
 */
interface ChatMessage {
  role: 'system' | 'user' | 'assistant' | 'function';
  content: string;
  name?: string;
}

/**
 * Options for text generation.
 */
interface GenerationOptions {
  systemPrompt?: string;
  providerId?: string;
  modelId?: string;
  contextId?: string;
  temperature?: number;
  maxTokens?: number;
  stopSequences?: string[];
  timeout?: number;
}

/**
 * Options for streaming text generation.
 */
interface StreamingOptions extends GenerationOptions {
  onComplete?: () => void;
  onError?: (error: Error) => void;
}

/**
 * Response from a text generation request.
 */
interface CompletionResponse {
  content: string;
  model: string;
  provider: string;
  finishReason?: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  contextId: string;
  timestamp: string;
}

/**
 * A chunk of a streaming response.
 */
interface StreamingChunk {
  chunk: string;
  contextId: string;
  model: string;
  provider: string;
  timestamp: string;
  done: boolean;
  error?: string;
}

/**
 * Information about an LLM model.
 */
interface ModelInfo {
  id: string;
  name: string;
  contextLength?: number;
  description?: string;
}

/**
 * Information about an LLM provider.
 */
interface ProviderInfo {
  name: string;
  available: boolean;
  models: ModelInfo[];
  description?: string;
}

/**
 * Information about all available LLM providers.
 */
interface ProvidersResponse {
  providers: Record<string, ProviderInfo>;
  default_provider: string;
  default_model: string;
}

/**
 * Options for initializing the TektonLLMClient.
 */
interface TektonLLMClientOptions {
  componentId: string;
  rhetorUrl?: string;
  rhetorWsUrl?: string;
  providerId?: string;
  modelId?: string;
  timeout?: number;
  authToken?: string;
  debug?: boolean;
}

/**
 * Client for interacting with Tekton LLM services.
 */
declare class TektonLLMClient {
  /**
   * Create a new TektonLLMClient.
   */
  constructor(options: TektonLLMClientOptions);
  
  /**
   * Generate text using the LLM.
   */
  generateText(prompt: string, options?: GenerationOptions): Promise<CompletionResponse>;
  
  /**
   * Generate a chat response using the LLM.
   */
  generateChatResponse(messages: ChatMessage[], options?: GenerationOptions): Promise<CompletionResponse>;
  
  /**
   * Stream text using the LLM.
   */
  streamText(prompt: string, onChunk: (chunk: StreamingChunk) => void, options?: StreamingOptions): string;
  
  /**
   * Stream a chat response using the LLM.
   */
  streamChatResponse(messages: ChatMessage[], onChunk: (chunk: StreamingChunk) => void, options?: StreamingOptions): string;
  
  /**
   * Cancel an ongoing streaming request.
   */
  cancelRequest(requestId: string): boolean;
  
  /**
   * Get available LLM providers and models.
   */
  getProviders(): Promise<ProvidersResponse>;
}

export { 
  TektonLLMClient,
  ChatMessage,
  GenerationOptions,
  StreamingOptions,
  CompletionResponse,
  StreamingChunk,
  ModelInfo,
  ProviderInfo,
  ProvidersResponse,
  TektonLLMClientOptions
};