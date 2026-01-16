# Elite RAG Server - Postman GraphQL 測試指南

## 基本設定

### 1. 建立 Postman Request

1. 開啟 Postman
2. 建立新 Request
3. 設定：
   - **Method**: `POST`
   - **URL**: `http://localhost:8000/graphql`
   - **Headers**:
     ```
     Content-Type: application/json
     ```

### 2. GraphQL 請求格式

所有 GraphQL 請求都使用相同的 JSON 結構：

```json
{
  "query": "你的 GraphQL 查詢",
  "variables": {
    "變數名稱": "變數值"
  }
}
```

---

## API 測試範例

### 健康檢查 (無需認證)

**Body (raw JSON):**
```json
{
  "query": "query { health }"
}
```

**預期回應:**
```json
{
  "data": {
    "health": "ok"
  }
}
```

---

## 認證相關

### 註冊新用戶

**Body:**
```json
{
  "query": "mutation Register($input: RegisterInput!) { register(input: $input) { token user { id email name } } }",
  "variables": {
    "input": {
      "email": "test@example.com",
      "password": "password123",
      "name": "Test User"
    }
  }
}
```

**預期回應:**
```json
{
  "data": {
    "register": {
      "token": "eyJ...",
      "user": {
        "id": "uuid-here",
        "email": "test@example.com",
        "name": "Test User"
      }
    }
  }
}
```

### 用戶登入

**Body:**
```json
{
  "query": "mutation Login($input: LoginInput!) { login(input: $input) { token user { id email name } } }",
  "variables": {
    "input": {
      "email": "test@example.com",
      "password": "password123"
    }
  }
}
```

**預期回應:**
```json
{
  "data": {
    "login": {
      "token": "eyJ...",
      "user": {
        "id": "uuid-here",
        "email": "test@example.com",
        "name": "Test User"
      }
    }
  }
}
```

---

## 需要認證的 API

> 在 Headers 加入 Authorization:
> ```
> Authorization: Bearer <你的 token>
> ```

### 建立文件

**Headers:**
```
Content-Type: application/json
Authorization: Bearer eyJ...
```

**Body:**
```json
{
  "query": "mutation CreateDocument($input: CreateDocumentInput!) { createDocument(input: $input) { id title content createdAt } }",
  "variables": {
    "input": {
      "title": "我的第一份文件",
      "content": "這是文件內容，將會被向量化索引以支援語意搜尋。"
    }
  }
}
```

**預期回應:**
```json
{
  "data": {
    "createDocument": {
      "id": "uuid-here",
      "title": "我的第一份文件",
      "content": "這是文件內容...",
      "createdAt": "2024-01-15T10:30:00"
    }
  }
}
```

### 查詢文件列表

**Body:**
```json
{
  "query": "query Documents($limit: Int, $offset: Int) { documents(limit: $limit, offset: $offset) { id title content createdAt } }",
  "variables": {
    "limit": 10,
    "offset": 0
  }
}
```

### 查詢單一文件

**Body:**
```json
{
  "query": "query Document($id: ID!) { document(id: $id) { id title content ownerId createdAt updatedAt } }",
  "variables": {
    "id": "your-document-uuid"
  }
}
```

### 更新文件

**Body:**
```json
{
  "query": "mutation UpdateDocument($input: UpdateDocumentInput!) { updateDocument(input: $input) { id title content updatedAt } }",
  "variables": {
    "input": {
      "id": "your-document-uuid",
      "title": "更新後的標題",
      "content": "更新後的內容"
    }
  }
}
```

### 刪除文件

**Body:**
```json
{
  "query": "mutation DeleteDocument($id: ID!) { deleteDocument(id: $id) }",
  "variables": {
    "id": "your-document-uuid"
  }
}
```

**預期回應:**
```json
{
  "data": {
    "deleteDocument": true
  }
}
```

---

## 搜尋功能

### 語意搜尋文件

**Body:**
```json
{
  "query": "query SearchDocuments($input: SearchDocumentsInput!) { searchDocuments(input: $input) { documentId title contentPreview score } }",
  "variables": {
    "input": {
      "query": "Python API 開發",
      "limit": 10,
      "threshold": 0.5
    }
  }
}
```

**預期回應:**
```json
{
  "data": {
    "searchDocuments": [
      {
        "documentId": "uuid-1",
        "title": "Python FastAPI 教學",
        "contentPreview": "FastAPI 是現代的 Python API 框架...",
        "score": 0.89
      },
      {
        "documentId": "uuid-2",
        "title": "RESTful API 設計",
        "contentPreview": "設計良好的 API 應該...",
        "score": 0.72
      }
    ]
  }
}
```

### 找出相似文件

**Body:**
```json
{
  "query": "query SimilarDocuments($input: FindSimilarInput!) { similarDocuments(input: $input) { documentId title similarityScore } }",
  "variables": {
    "input": {
      "documentId": "your-document-uuid",
      "limit": 5
    }
  }
}
```

---

## Postman Collection 設定建議

### 環境變數

建立 Environment 並設定：

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| `base_url` | `http://localhost:8000` | `http://localhost:8000` |
| `token` | (空白) | (登入後自動填入) |

### 自動設定 Token

在 Login 請求的 **Tests** tab 加入：

```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    if (jsonData.data && jsonData.data.login) {
        pm.environment.set("token", jsonData.data.login.token);
    }
}
```

### 使用環境變數

**URL:** `{{base_url}}/graphql`

**Headers:**
```
Authorization: Bearer {{token}}
```

---

## 錯誤處理

### 未認證錯誤

```json
{
  "data": null,
  "errors": [
    {
      "message": "User is not authenticated",
      "extensions": {
        "code": "UNAUTHENTICATED"
      }
    }
  ]
}
```

### 驗證錯誤

```json
{
  "data": null,
  "errors": [
    {
      "message": "Email already registered",
      "extensions": {
        "code": "VALIDATION_ERROR"
      }
    }
  ]
}
```

### 資源未找到

```json
{
  "data": null,
  "errors": [
    {
      "message": "Document not found",
      "extensions": {
        "code": "NOT_FOUND"
      }
    }
  ]
}
```

---

## 測試流程建議

1. **健康檢查** - 確認伺服器運作
2. **註冊用戶** - 建立測試帳號
3. **登入** - 取得 Token
4. **建立文件** - 新增測試資料
5. **語意搜尋** - 測試向量搜尋功能
6. **相似文件** - 測試相似度比對
7. **更新/刪除** - 測試完整 CRUD

---

## GraphQL Playground 替代方案

伺服器也提供內建 GraphQL IDE：

瀏覽器開啟: `http://localhost:8000/graphql`

可直接在網頁介面測試查詢，無需 Postman。
