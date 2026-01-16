"""
OpenAI 嵌入服務（可選）

ABP 對比：
- ABP: public class OpenAIEmbeddingService : IEmbeddingService, ITransientDependency
- 使用 IHttpClientFactory 呼叫 OpenAI API
- 需要配置 OpenAI API Key

注意：此為可選功能，需要安裝 openai 套件
uv add openai
"""

from src.infrastructure.embeddings.base import IEmbeddingService
from src.config import settings


class OpenAIEmbeddingService(IEmbeddingService):
    """
    使用 OpenAI API 的嵌入服務

    ABP 對比：
    - ABP: public class OpenAIEmbeddingService : IEmbeddingService
    - ABP 使用 IHttpClientFactory 管理 HTTP 連線
    - Python: 使用 openai SDK

    模型說明：
    - text-embedding-3-small: 1536 維，性價比高
    - text-embedding-3-large: 3072 維，最高品質
    """

    # 模型維度對照表
    MODEL_DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        """
        初始化 OpenAI 嵌入服務

        ABP 對比（使用建構式注入）：
        public OpenAIEmbeddingService(
            IOptions<OpenAIOptions> options,
            IHttpClientFactory httpClientFactory)
        """
        self._api_key = api_key or settings.openai_api_key
        self._model = model or settings.openai_embedding_model
        self._client = None

        if not self._api_key:
            raise ValueError(
                "OpenAI API key is required. "
                "Set OPENAI_API_KEY in .env or pass api_key parameter."
            )

    def _get_client(self):
        """
        懶載入 OpenAI 客戶端

        ABP 對比：
        - ABP 使用 IHttpClientFactory.CreateClient()
        - Python: 直接實例化 OpenAI 客戶端
        """
        if self._client is None:
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=self._api_key)
            except ImportError:
                raise ImportError(
                    "openai package is required for OpenAI embeddings. "
                    "Install with: uv add openai"
                )
        return self._client

    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        使用 OpenAI API 生成嵌入向量

        ABP 對比：
        public async Task<List<float[]>> GenerateEmbeddingsAsync(List<string> texts)
        {
            var response = await _httpClient.PostAsJsonAsync(...);
            return response.Data.Select(d => d.Embedding).ToList();
        }
        """
        client = self._get_client()
        response = client.embeddings.create(
            model=self._model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    @property
    def dimension(self) -> int:
        """
        嵌入向量的維度

        ABP 對比：
        public int Dimension => ModelDimensions[_model];
        """
        return self.MODEL_DIMENSIONS.get(self._model, 1536)
