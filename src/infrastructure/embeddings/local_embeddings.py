"""
本地嵌入服務（使用 sentence-transformers）

ABP 對比：
- ABP: public class LocalEmbeddingService : IEmbeddingService, ITransientDependency
- 這是免費的本地嵌入方案，無需 API Key
- 使用 all-MiniLM-L6-v2 模型，輸出 384 維向量
"""
from functools import lru_cache

from src.infrastructure.embeddings.base import IEmbeddingService
from src.config import settings


class LocalEmbeddingService(IEmbeddingService):
    """
    使用 sentence-transformers 的本地嵌入服務

    ABP 對比：
    - ABP: public class LocalEmbeddingService : IEmbeddingService
    - ABP 可能會使用屬性注入 IOptions<EmbeddingOptions>
    - Python: 直接從 settings 讀取配置

    模型說明：
    - all-MiniLM-L6-v2: 384 維，速度快，適合一般用途
    - paraphrase-multilingual-MiniLM-L12-v2: 384 維，多語言支援
    """

    def __init__(self, model_name: str | None = None):
        """
        初始化嵌入服務

        ABP 對比（使用建構式注入）：
        public LocalEmbeddingService(IOptions<EmbeddingOptions> options)
        {
            _modelName = options.Value.ModelName;
        }
        """
        self._model_name = model_name or settings.embedding_model
        self._model = None
        self._dimension = settings.embedding_dimension

    def _get_model(self):
        """
        懶載入模型（第一次使用時才載入）

        ABP 對比：
        - ABP 可能在 OnApplicationInitializationAsync 中預載入
        - Python 使用懶載入避免啟動時間過長
        """
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
            # 更新實際維度
            self._dimension = self._model.get_sentence_embedding_dimension()
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        將文本列表轉換為嵌入向量

        ABP 對比：
        public async Task<List<float[]>> GenerateEmbeddingsAsync(List<string> texts)
        {
            return await Task.Run(() => _model.Encode(texts));
        }

        注意：sentence-transformers 是 CPU 密集型操作
        在生產環境中可能需要使用 worker pool 或 GPU
        """
        model = self._get_model()
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        """
        嵌入向量的維度

        ABP 對比：
        public int Dimension => _model?.GetSentenceEmbeddingDimension() ?? 384;
        """
        return self._dimension


@lru_cache(maxsize=1)
def get_embedding_service() -> IEmbeddingService:
    """
    取得嵌入服務實例（Singleton）

    ABP 對比：
    - ABP: services.AddSingleton<IEmbeddingService, LocalEmbeddingService>()
    - Python: 使用 lru_cache 實現 Singleton
    """
    if settings.embedding_provider == "openai":
        from src.infrastructure.embeddings.openai_embeddings import OpenAIEmbeddingService

        return OpenAIEmbeddingService()
    return LocalEmbeddingService()
