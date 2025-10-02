import { api } from "./index";

export const generateText = async (
  prompt,
  temperature = 0.7,
  maxTokens = 2048,
  model = "deepseek-chat"
) => {
  try {
    const response = await api.post("/ai/deepseek/generate/", {
      prompt,
      temperature,
      max_tokens: maxTokens,
      model,
    });
    return response.data;
  } catch (error) {
    console.error("AI服务调用失败:", error);
    throw error;
  }
};

export const chatCompletion = async (
  messages,
  model = "deepseek-chat",
  temperature = 0.7,
  maxTokens = 2048
) => {
  try {
    const response = await api.post("/ai/deepseek/chat/", {
      messages,
      model,
      temperature,
      max_tokens: maxTokens,
    });
    return response.data;
  } catch (error) {
    console.error("AI对话服务调用失败:", error);
    throw error;
  }
};
