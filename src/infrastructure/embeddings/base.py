"""
嵌入服務介面

ABP 對比：
- ABP: public interface IEmbeddingService : ITransientDependency
- 定義於 Domain 或 Application.Contracts 層
- 實作可能包含 OpenAIEmbeddingService、LocalEmbeddingService
- 使用 ABP 的 Named Option 或 Factory Pattern 切換實作
"""
from abc import ABC, abstractmethod


class IEmbeddingService(ABC):
    """
    嵌入服務介面

    ABP 對比：
    - ABP: public interface IEmbeddingService : ITransientDependency
    - Python ABC 類似 C# interface
    """

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        將文本轉換為嵌入向量

        ABP 對比：
        - ABP: Task<List<float[]>> GenerateEmbeddingsAsync(List<string> texts)
        - 這裡使用同步方法，因為 sentence-transformers 是 CPU 密集型
        - 可以考慮使用 run_in_executor 包裝為非同步
        """
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        嵌入向量的維度

        ABP 對比：
        - ABP: int Dimension { get; }
        """
        ...

    def embed_single(self, text: str) -> list[float]:
        """
        便利方法：嵌入單一文本

        ABP 對比：
        - ABP 可能會有 GenerateEmbeddingAsync(string text) 單一版本
        """
        return self.embed([text])[0]
