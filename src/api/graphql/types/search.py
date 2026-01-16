"""
搜尋相關 GraphQL 類型

ABP/HotChocolate 對比：
- HotChocolate: [ObjectType] 或 record 搭配 [GraphQLType]
- Python Strawberry: @strawberry.type 裝飾器
"""

import strawberry


@strawberry.type
class SearchResultType:
    """
    語意搜尋結果類型

    ABP/HotChocolate 對比：
    [ObjectType]
    public class SearchResultType
    {
        public Guid DocumentId { get; set; }
        public string Title { get; set; }
        public string ContentPreview { get; set; }
        public float Score { get; set; }
    }
    """

    document_id: strawberry.ID
    title: str
    content_preview: str
    score: float


@strawberry.type
class SimilarDocumentType:
    """
    相似文件類型

    ABP/HotChocolate 對比：
    [ObjectType]
    public class SimilarDocumentType
    {
        public Guid DocumentId { get; set; }
        public string Title { get; set; }
        public float SimilarityScore { get; set; }
    }
    """

    document_id: strawberry.ID
    title: str
    similarity_score: float


@strawberry.input
class SearchDocumentsInput:
    """
    語意搜尋輸入

    ABP/HotChocolate 對比：
    [InputType]
    public class SearchDocumentsInput
    {
        [Required]
        public string Query { get; set; }
        public int Limit { get; set; } = 10;
        public float? Threshold { get; set; }
    }
    """

    query: str
    limit: int = 10
    threshold: float | None = None


@strawberry.input
class FindSimilarInput:
    """
    找出相似文件輸入

    ABP/HotChocolate 對比：
    [InputType]
    public class FindSimilarInput
    {
        [Required]
        public Guid DocumentId { get; set; }
        public int Limit { get; set; } = 5;
    }
    """

    document_id: strawberry.ID
    limit: int = 5
