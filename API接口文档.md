# Multi-Model Routing System API 接口文档

## 1. 用户登录页面接口

### 1.1 用户登录

**接口描述**：用户通过用户名/邮箱和密码进行身份验证，获取访问令牌。

**请求信息**

- **URL**: `/api/v1/auth/login`
- **方法**: `POST`
- **Content-Type**: `application/json`

**请求参数**

| 参数名   | 类型   | 必填 | 说明                         |
| -------- | ------ | ---- | ---------------------------- |
| username | string | 否   | 用户名（与email二选一）      |
| email    | string | 否   | 邮箱地址（与username二选一） |
| password | string | 是   | 用户密码                     |

**请求示例**

```json
{
  "username": "user123",
  "password": "password123"
}
```

或

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应参数**

| 参数名             | 类型    | 说明                            |
| ------------------ | ------- | ------------------------------- |
| success            | boolean | 请求是否成功                    |
| message            | string  | 响应消息                        |
| data               | object  | 响应数据                        |
| data.token         | string  | JWT访问令牌                     |
| data.refresh_token | string  | 刷新令牌（可选）                |
| data.user_id       | string  | 用户ID                          |
| data.username      | string  | 用户名                          |
| data.email         | string  | 邮箱地址                        |
| data.role          | string  | 用户角色：`user` 或 `admin` |
| data.expires_in    | integer | 令牌过期时间（秒）              |

**成功响应示例** (200 OK)

```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "refresh_token_string",
    "user_id": "user_123456",
    "username": "user123",
    "email": "user@example.com",
    "role": "user",
    "expires_in": 3600
  }
}
```

**错误响应示例** (401 Unauthorized)

```json
{
  "success": false,
  "message": "用户名或密码错误",
  "error_code": "AUTH_001",
  "data": null
}
```

**错误码说明**

| 错误码   | HTTP状态码 | 说明                         |
| -------- | ---------- | ---------------------------- |
| AUTH_001 | 401        | 用户名或密码错误             |
| AUTH_002 | 400        | 请求参数缺失或格式错误       |
| AUTH_003 | 429        | 登录尝试次数过多，请稍后再试 |
| AUTH_004 | 500        | 服务器内部错误               |

---

### 1.2 获取当前用户信息

**接口描述**：通过JWT令牌获取当前登录用户的详细信息。

**请求信息**

- **URL**: `/api/v1/auth/user`
- **方法**: `GET`
- **Headers**:
  - `Authorization: Bearer {token}`

**请求参数**

无（通过Header中的token进行身份验证）

**响应参数**

| 参数名          | 类型    | 说明                         |
| --------------- | ------- | ---------------------------- |
| success         | boolean | 请求是否成功                 |
| message         | string  | 响应消息                     |
| data            | object  | 用户信息                     |
| data.user_id    | string  | 用户ID                       |
| data.username   | string  | 用户名                       |
| data.email      | string  | 邮箱地址                     |
| data.role       | string  | 用户角色                     |
| data.created_at | string  | 账户创建时间（ISO 8601格式） |
| data.last_login | string  | 最后登录时间（ISO 8601格式） |

**成功响应示例** (200 OK)

```json
{
  "success": true,
  "message": "获取用户信息成功",
  "data": {
    "user_id": "user_123456",
    "username": "user123",
    "email": "user@example.com",
    "role": "user",
    "created_at": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-20T14:25:00Z"
  }
}
```

**错误响应示例** (401 Unauthorized)

```json
{
  "success": false,
  "message": "令牌无效或已过期",
  "error_code": "AUTH_005",
  "data": null
}
```

---

### 1.3 刷新访问令牌

**接口描述**：使用刷新令牌获取新的访问令牌。

**请求信息**

- **URL**: `/api/v1/auth/refresh`
- **方法**: `POST`
- **Content-Type**: `application/json`

**请求参数**

| 参数名        | 类型   | 必填 | 说明     |
| ------------- | ------ | ---- | -------- |
| refresh_token | string | 是   | 刷新令牌 |

**请求示例**

```json
{
  "refresh_token": "refresh_token_string"
}
```

**响应参数**

| 参数名          | 类型    | 说明               |
| --------------- | ------- | ------------------ |
| success         | boolean | 请求是否成功       |
| message         | string  | 响应消息           |
| data            | object  | 响应数据           |
| data.token      | string  | 新的JWT访问令牌    |
| data.expires_in | integer | 令牌过期时间（秒） |

**成功响应示例** (200 OK)

```json
{
  "success": true,
  "message": "令牌刷新成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600
  }
}
```

---

### 1.4 用户登出

**接口描述**：用户登出，使当前令牌失效。

**请求信息**

- **URL**: `/api/v1/auth/logout`
- **方法**: `POST`
- **Headers**:
  - `Authorization: Bearer {token}`

**请求参数**

无

**响应参数**

| 参数名  | 类型    | 说明         |
| ------- | ------- | ------------ |
| success | boolean | 请求是否成功 |
| message | string  | 响应消息     |

**成功响应示例** (200 OK)

```json
{
  "success": true,
  "message": "登出成功"
}
```

---

## 2. 管理员上传新模型页面接口

### 2.1 上传新模型

**接口描述**：管理员添加新的LLM模型到路由系统中。系统会自动计算模型的能力向量（z_M）并注册到模型库。

**请求信息**

- **URL**: `/api/v1/admin/models`
- **方法**: `POST`
- **Content-Type**: `application/json`
- **Headers**:
  - `Authorization: Bearer {admin_token}`

**请求参数**

| 参数名                       | 类型    | 必填 | 说明                                                                  |
| ---------------------------- | ------- | ---- | --------------------------------------------------------------------- |
| model_name                   | string  | 是   | 模型名称（唯一标识）                                                  |
| model_description            | string  | 否   | 模型描述                                                              |
| model_provider               | string  | 否   | 模型提供商（如：OpenAI, Anthropic等）                                 |
| probe_scores                 | array   | 是   | 探测集分数数组                                                        |
| probe_scores[].task_type     | string  | 是   | 任务类型：`chat`, `code`, `math`, `translation`, `tool_use` |
| probe_scores[].score         | float   | 是   | 该任务类型的得分（0.0-1.0）                                           |
| metadata                     | object  | 是   | 模型元数据                                                            |
| metadata.cost_per_1k_tokens  | float   | 是   | 每1000个token的成本（美元）                                           |
| metadata.latency_p50_ms      | integer | 是   | 50分位延迟（毫秒）                                                    |
| metadata.safety_rating       | integer | 是   | 安全性评级（1-5，5最安全）                                            |
| metadata.max_context_length  | integer | 是   | 最大上下文长度（token数）                                             |
| metadata.tenant_availability | array   | 否   | 可用的租户ID列表，为空表示所有租户可用                                |
| metadata.api_endpoint        | string  | 否   | 模型API端点URL                                                        |
| metadata.api_key_required    | boolean | 否   | 是否需要API密钥                                                       |

**请求示例**

```json
{
  "model_name": "gpt-4-turbo",
  "model_description": "OpenAI GPT-4 Turbo model",
  "model_provider": "OpenAI",
  "probe_scores": [
    {
      "task_type": "chat",
      "score": 0.95
    },
    {
      "task_type": "code",
      "score": 0.92
    },
    {
      "task_type": "math",
      "score": 0.88
    },
    {
      "task_type": "translation",
      "score": 0.90
    },
    {
      "task_type": "tool_use",
      "score": 0.93
    }
  ],
  "metadata": {
    "cost_per_1k_tokens": 0.01,
    "latency_p50_ms": 500,
    "safety_rating": 5,
    "max_context_length": 128000,
    "tenant_availability": ["tenant_A", "tenant_B"],
    "api_endpoint": "https://api.openai.com/v1/chat/completions",
    "api_key_required": true
  }
}
```

**响应参数**

| 参数名          | 类型    | 说明                                            |
| --------------- | ------- | ----------------------------------------------- |
| success         | boolean | 请求是否成功                                    |
| message         | string  | 响应消息                                        |
| data            | object  | 响应数据                                        |
| data.model_id   | string  | 新创建的模型ID                                  |
| data.model_name | string  | 模型名称                                        |
| data.z_M        | array   | 模型能力向量（z_M），浮点数数组                 |
| data.z_M_dim    | integer | 能力向量维度                                    |
| data.status     | string  | 模型状态：`active`, `pending`, `inactive` |
| data.created_at | string  | 创建时间（ISO 8601格式）                        |

**成功响应示例** (201 Created)

```json
{
  "success": true,
  "message": "模型上传成功",
  "data": {
    "model_id": "model_abc123",
    "model_name": "gpt-4-turbo",
    "z_M": [0.12, -0.34, 0.56, 0.78, ...],
    "z_M_dim": 128,
    "status": "active",
    "created_at": "2024-01-20T15:30:00Z"
  }
}
```

**错误响应示例** (400 Bad Request)

```json
{
  "success": false,
  "message": "模型名称已存在",
  "error_code": "ADMIN_001",
  "data": null
}
```

**错误码说明**

| 错误码    | HTTP状态码 | 说明                     |
| --------- | ---------- | ------------------------ |
| ADMIN_001 | 400        | 模型名称已存在           |
| ADMIN_002 | 400        | 请求参数缺失或格式错误   |
| ADMIN_003 | 400        | 探测集分数格式错误       |
| ADMIN_004 | 403        | 权限不足，需要管理员权限 |
| ADMIN_005 | 500        | 模型编码失败             |
| ADMIN_006 | 500        | 服务器内部错误           |

---

### 2.2 更新模型信息

**接口描述**：管理员更新已存在模型的信息（元数据、探测集分数等）。

**请求信息**

- **URL**: `/api/v1/admin/models/{model_id}`
- **方法**: `PUT`
- **Content-Type**: `application/json`
- **Headers**:
  - `Authorization: Bearer {admin_token}`

**路径参数**

| 参数名   | 类型   | 必填 | 说明                  |
| -------- | ------ | ---- | --------------------- |
| model_id | string | 是   | 模型ID（URL路径参数） |

**请求参数**

所有字段均为可选，只更新提供的字段：

| 参数名            | 类型   | 必填 | 说明                                      |
| ----------------- | ------ | ---- | ----------------------------------------- |
| model_name        | string | 否   | 模型名称                                  |
| model_description | string | 否   | 模型描述                                  |
| probe_scores      | array  | 否   | 探测集分数数组（如果提供，会重新计算z_M） |
| metadata          | object | 否   | 模型元数据（部分字段可更新）              |

**请求示例**

```json
{
  "metadata": {
    "cost_per_1k_tokens": 0.008,
    "latency_p50_ms": 450,
    "safety_rating": 5
  }
}
```

**响应参数**

| 参数名          | 类型    | 说明                     |
| --------------- | ------- | ------------------------ |
| success         | boolean | 请求是否成功             |
| message         | string  | 响应消息                 |
| data            | object  | 更新后的模型信息         |
| data.model_id   | string  | 模型ID                   |
| data.model_name | string  | 模型名称                 |
| data.updated_at | string  | 更新时间（ISO 8601格式） |

**成功响应示例** (200 OK)

```json
{
  "success": true,
  "message": "模型信息更新成功",
  "data": {
    "model_id": "model_abc123",
    "model_name": "gpt-4-turbo",
    "updated_at": "2024-01-20T16:00:00Z"
  }
}
```

**错误响应示例** (404 Not Found)

```json
{
  "success": false,
  "message": "模型不存在",
  "error_code": "ADMIN_007",
  "data": null
}
```

---

### 2.3 删除模型

**接口描述**：管理员删除指定的模型（软删除，标记为inactive状态）。

**请求信息**

- **URL**: `/api/v1/admin/models/{model_id}`
- **方法**: `DELETE`
- **Headers**:
  - `Authorization: Bearer {admin_token}`

**路径参数**

| 参数名   | 类型   | 必填 | 说明                  |
| -------- | ------ | ---- | --------------------- |
| model_id | string | 是   | 模型ID（URL路径参数） |

**请求参数**

无

**响应参数**

| 参数名        | 类型    | 说明                       |
| ------------- | ------- | -------------------------- |
| success       | boolean | 请求是否成功               |
| message       | string  | 响应消息                   |
| data          | object  | 响应数据                   |
| data.model_id | string  | 被删除的模型ID             |
| data.status   | string  | 删除后的状态：`inactive` |

**成功响应示例** (200 OK)

```json
{
  "success": true,
  "message": "模型删除成功",
  "data": {
    "model_id": "model_abc123",
    "status": "inactive"
  }
}
```

**错误响应示例** (404 Not Found)

```json
{
  "success": false,
  "message": "模型不存在",
  "error_code": "ADMIN_007",
  "data": null
}
```

---

### 2.4 获取所有模型列表（管理员视图）

**接口描述**：管理员获取系统中所有模型的完整信息列表，包括已删除的模型。

**请求信息**

- **URL**: `/api/v1/admin/models`
- **方法**: `GET`
- **Headers**:
  - `Authorization: Bearer {admin_token}`

**查询参数**

| 参数名 | 类型    | 必填 | 说明                                                            |
| ------ | ------- | ---- | --------------------------------------------------------------- |
| status | string  | 否   | 筛选状态：`active`, `inactive`, `pending`，不传则返回所有 |
| limit  | integer | 否   | 每页数量，默认20，最大100                                       |
| offset | integer | 否   | 偏移量，默认0                                                   |
| search | string  | 否   | 搜索关键词（模型名称或描述）                                    |

**响应参数**

| 参数名                          | 类型    | 说明         |
| ------------------------------- | ------- | ------------ |
| success                         | boolean | 请求是否成功 |
| message                         | string  | 响应消息     |
| data                            | object  | 响应数据     |
| data.models                     | array   | 模型列表     |
| data.models[].model_id          | string  | 模型ID       |
| data.models[].model_name        | string  | 模型名称     |
| data.models[].model_description | string  | 模型描述     |
| data.models[].status            | string  | 模型状态     |
| data.models[].metadata          | object  | 模型元数据   |
| data.models[].created_at        | string  | 创建时间     |
| data.models[].updated_at        | string  | 更新时间     |
| data.total                      | integer | 总记录数     |
| data.limit                      | integer | 每页数量     |
| data.offset                     | integer | 偏移量       |

**成功响应示例** (200 OK)

```json
{
  "success": true,
  "message": "获取模型列表成功",
  "data": {
    "models": [
      {
        "model_id": "model_abc123",
        "model_name": "gpt-4-turbo",
        "model_description": "OpenAI GPT-4 Turbo model",
        "status": "active",
        "metadata": {
          "cost_per_1k_tokens": 0.01,
          "latency_p50_ms": 500,
          "safety_rating": 5,
          "max_context_length": 128000
        },
        "created_at": "2024-01-20T15:30:00Z",
        "updated_at": "2024-01-20T15:30:00Z"
      }
    ],
    "total": 10,
    "limit": 20,
    "offset": 0
  }
}
```

---

### 2.5 获取单个模型详情（管理员视图）

**接口描述**：管理员获取指定模型的完整详细信息，包括能力向量。

**请求信息**

- **URL**: `/api/v1/admin/models/{model_id}`
- **方法**: `GET`
- **Headers**:
  - `Authorization: Bearer {admin_token}`

**路径参数**

| 参数名   | 类型   | 必填 | 说明                  |
| -------- | ------ | ---- | --------------------- |
| model_id | string | 是   | 模型ID（URL路径参数） |

**响应参数**

| 参数名                 | 类型    | 说明         |
| ---------------------- | ------- | ------------ |
| success                | boolean | 请求是否成功 |
| message                | string  | 响应消息     |
| data                   | object  | 模型完整信息 |
| data.model_id          | string  | 模型ID       |
| data.model_name        | string  | 模型名称     |
| data.model_description | string  | 模型描述     |
| data.model_provider    | string  | 模型提供商   |
| data.probe_scores      | array   | 探测集分数   |
| data.z_M               | array   | 模型能力向量 |
| data.z_M_dim           | integer | 能力向量维度 |
| data.metadata          | object  | 模型元数据   |
| data.status            | string  | 模型状态     |
| data.created_at        | string  | 创建时间     |
| data.updated_at        | string  | 更新时间     |

**成功响应示例** (200 OK)

```json
{
  "success": true,
  "message": "获取模型详情成功",
  "data": {
    "model_id": "model_abc123",
    "model_name": "gpt-4-turbo",
    "model_description": "OpenAI GPT-4 Turbo model",
    "model_provider": "OpenAI",
    "probe_scores": [
      {"task_type": "chat", "score": 0.95},
      {"task_type": "code", "score": 0.92},
      {"task_type": "math", "score": 0.88},
      {"task_type": "translation", "score": 0.90},
      {"task_type": "tool_use", "score": 0.93}
    ],
    "z_M": [0.12, -0.34, 0.56, 0.78, ...],
    "z_M_dim": 128,
    "metadata": {
      "cost_per_1k_tokens": 0.01,
      "latency_p50_ms": 500,
      "safety_rating": 5,
      "max_context_length": 128000,
      "tenant_availability": ["tenant_A", "tenant_B"]
    },
    "status": "active",
    "created_at": "2024-01-20T15:30:00Z",
    "updated_at": "2024-01-20T15:30:00Z"
  }
}
```

---

## 3. Query路由选择页面接口

### 3.1 Query Embedding（Step 1：展示用向量生成）

**接口描述**：将用户输入的自然语言Query转换为展示用的embedding向量。该向量用于UI展示和可解释性分析，不直接用于模型匹配。

**请求信息**

- **URL**: `/api/v1/router/embed`
- **方法**: `POST`
- **Content-Type**: `application/json`
- **Headers**:
  - `Authorization: Bearer {token}`

**请求参数**

| 参数名     | 类型   | 必填 | 说明                                                                                                  |
| ---------- | ------ | ---- | ----------------------------------------------------------------------------------------------------- |
| query_text | string | 是   | 用户输入的自然语言查询文本                                                                            |
| query_tags | array  | 否   | Query属性标签数组，可选值：`code`, `reasoning`, `creative`, `data`, `translation`, `math` |

**请求示例**

```json
{
  "query_text": "Write a Python function to calculate fibonacci numbers",
  "query_tags": ["code", "reasoning"]
}
```

**响应参数**

| 参数名                 | 类型    | 说明                               |
| ---------------------- | ------- | ---------------------------------- |
| success                | boolean | 请求是否成功                       |
| message                | string  | 响应消息                           |
| data                   | object  | 响应数据                           |
| data.embedding_vector  | array   | 1D embedding向量（浮点数数组）     |
| data.embedding_dim     | integer | embedding向量维度                  |
| data.embedding_heatmap | array   | 2D heatmap数据（可选，用于UI展示） |
| data.query_text        | string  | 原始查询文本（回显）               |
| data.query_tags        | array   | 查询标签（回显）                   |

**成功响应示例** (200 OK)

```json
{
  "success": true,
  "message": "Query embedding生成成功",
  "data": {
    "embedding_vector": [0.12, -0.34, 0.56, 0.78, ...],
    "embedding_dim": 384,
    "embedding_heatmap": [
      [0.1, 0.2, 0.3, ...],
      [0.4, 0.5, 0.6, ...],
      ...
    ],
    "query_text": "Write a Python function to calculate fibonacci numbers",
    "query_tags": ["code", "reasoning"]
  }
}
```

**错误响应示例** (400 Bad Request)

```json
{
  "success": false,
  "message": "查询文本不能为空",
  "error_code": "ROUTER_001",
  "data": null
}
```

---

### 3.2 Query Encoding（Step 2：匹配向量生成）

**接口描述**：将Query Embedding编码为QVector（Query能力向量）。QVector与模型侧的z_M位于同一能力空间，是后续路由计算的唯一Query表示。

**请求信息**

- **URL**: `/api/v1/router/encode`
- **方法**: `POST`
- **Content-Type**: `application/json`
- **Headers**:
  - `Authorization: Bearer {token}`

**请求参数**

| 参数名           | 类型   | 必填 | 说明                                                             |
| ---------------- | ------ | ---- | ---------------------------------------------------------------- |
| query_text       | string | 是   | 原始查询文本（用于embedding生成和可解释特征提取）                |
| embedding_vector | array  | 否   | 来自Step 1的embedding向量（可选，提供时可跳过embedding生成步骤） |
| tenant_id        | string | 否   | 租户ID（用于租户偏好配置）                                       |

**参数说明**：

- `query_text`：必填，用于生成embedding和提取可解释特征
- `embedding_vector`：可选，如果提供则直接使用，否则从 `query_text`生成
- 推荐用法：如果已调用Step 1获取embedding，可传入 `embedding_vector`以提升性能；否则仅提供 `query_text`即可

**请求示例**

```json
{
  "embedding_vector": [0.12, -0.34, 0.56, 0.78, ...],
  "query_text": "Write a Python function to calculate fibonacci numbers",
  "tenant_id": "tenant_A"
}
```

**响应参数**

| 参数名                                      | 类型    | 说明                        |
| ------------------------------------------- | ------- | --------------------------- |
| success                                     | boolean | 请求是否成功                |
| message                                     | string  | 响应消息                    |
| data                                        | object  | 响应数据                    |
| data.q_vector                               | array   | QVector（固定维度，如128D） |
| data.q_vector_dim                           | integer | QVector维度                 |
| data.activated_capability_dimensions        | array   | Top-K激活维度标签           |
| data.activation_scores                      | object  | 各维度激活分数（可选）      |
| data.interpretable_features                 | object  | 可解释特征（可选）          |
| data.interpretable_features.task_type       | array   | 检测到的任务类型            |
| data.interpretable_features.domain          | array   | 检测到的领域                |
| data.interpretable_features.reasoning_level | array   | 推理深度级别                |

**成功响应示例** (200 OK)

```json
{
  "success": true,
  "message": "Query encoding成功",
  "data": {
    "q_vector": [0.12, -0.34, 0.56, 0.78, ...],
    "q_vector_dim": 128,
    "activated_capability_dimensions": ["code", "math", "reasoning"],
    "activation_scores": {
      "code": 0.95,
      "math": 0.88,
      "reasoning": 0.92
    },
    "interpretable_features": {
      "task_type": ["code"],
      "domain": ["programming"],
      "reasoning_level": ["high"]
    }
  }
}
```

**错误响应示例** (400 Bad Request)

```json
{
  "success": false,
  "message": "embedding_vector格式错误",
  "error_code": "ROUTER_002",
  "data": null
}
```

**重要说明**：

- QVector是后续所有路由计算的唯一Query表示
- 不允许在路由阶段重新生成QVector
- 建议客户端缓存QVector，避免重复计算
- `query_text`为必填参数，用于生成embedding和提取可解释特征
- `embedding_vector`为可选参数，提供时可跳过embedding生成步骤，提升性能

---

### 3.3 获取候选模型列表（用户视图）

**接口描述**：获取系统中所有可用的候选模型列表，供用户选择参与路由。该接口返回用户视图，只包含active状态的模型。

**请求信息**

- **URL**: `/api/v1/router/models`
- **方法**: `GET`
- **Headers**:
  - `Authorization: Bearer {token}`

**查询参数**

| 参数名      | 类型    | 必填 | 说明                                                           |
| ----------- | ------- | ---- | -------------------------------------------------------------- |
| tenant_id   | string  | 否   | 租户ID（筛选该租户可用的模型）                                 |
| include_z_M | boolean | 否   | 是否包含模型能力向量z_M，默认false（仅返回元数据，不返回向量） |
| limit       | integer | 否   | 每页数量，默认50，最大100                                      |
| offset      | integer | 否   | 偏移量，默认0                                                  |

**参数说明**：

- `include_z_M=false`（默认）：仅返回模型元数据，不返回z_M向量，减少响应体积
- `include_z_M=true`：返回完整的z_M向量，用于客户端本地路由计算或可视化分析
- **注意**：z_M向量较大（128维浮点数组），仅在需要时请求

**响应参数**

| 参数名                                    | 类型    | 说明                                            |
| ----------------------------------------- | ------- | ----------------------------------------------- |
| success                                   | boolean | 请求是否成功                                    |
| message                                   | string  | 响应消息                                        |
| data                                      | object  | 响应数据                                        |
| data.models                               | array   | 模型列表                                        |
| data.models[].model_id                    | string  | 模型ID                                          |
| data.models[].model_name                  | string  | 模型名称                                        |
| data.models[].model_provider              | string  | 模型提供商                                      |
| data.models[].z_M                         | array   | 模型能力向量（z_M，仅当include_z_M=true时返回） |
| data.models[].z_M_dim                     | integer | 能力向量维度（仅当include_z_M=true时返回）      |
| data.models[].metadata                    | object  | 模型元数据                                      |
| data.models[].metadata.cost_per_1k_tokens | float   | 每1000个token的成本（美元）                     |
| data.models[].metadata.latency_p50_ms     | integer | 50分位延迟（毫秒）                              |
| data.models[].metadata.safety_rating      | integer | 安全性评级（1-5）                               |
| data.models[].metadata.max_context_length | integer | 最大上下文长度                                  |
| data.models[].status                      | string  | 模型状态（仅返回 `active`）                   |
| data.total                                | integer | 总记录数                                        |
| data.limit                                | integer | 每页数量                                        |
| data.offset                               | integer | 偏移量                                          |

**成功响应示例** (200 OK)

```json
{
  "success": true,
  "message": "获取模型列表成功",
  "data": {
    "models": [
      {
        "model_id": "model_abc123",
        "model_name": "gpt-4-turbo",
        "model_provider": "OpenAI",
        "z_M": [0.12, -0.34, 0.56, 0.78, ...],
        "z_M_dim": 128,
        "metadata": {
          "cost_per_1k_tokens": 0.01,
          "latency_p50_ms": 500,
          "safety_rating": 5,
          "max_context_length": 128000
        },
        "status": "active"
      },
      {
        "model_id": "model_def456",
        "model_name": "claude-3-opus",
        "model_provider": "Anthropic",
        "z_M": [0.23, -0.45, 0.67, 0.89, ...],
        "z_M_dim": 128,
        "metadata": {
          "cost_per_1k_tokens": 0.015,
          "latency_p50_ms": 600,
          "safety_rating": 5,
          "max_context_length": 200000
        },
        "status": "active"
      }
    ],
    "total": 10,
    "limit": 50,
    "offset": 0
  }
}
```

**错误响应示例** (401 Unauthorized)

```json
{
  "success": false,
  "message": "未授权访问",
  "error_code": "ROUTER_003",
  "data": null
}
```

---

### 3.4 获取模型详情（用户视图）

**接口描述**：获取指定模型的详细信息，包括能力向量和元数据。该接口用于模型详情弹窗展示。

**请求信息**

- **URL**: `/api/v1/router/models/{model_id}`
- **方法**: `GET`
- **Headers**:
  - `Authorization: Bearer {token}`

**路径参数**

| 参数名   | 类型   | 必填 | 说明                  |
| -------- | ------ | ---- | --------------------- |
| model_id | string | 是   | 模型ID（URL路径参数） |

**查询参数**

| 参数名          | 类型    | 必填 | 说明                                                          |
| --------------- | ------- | ---- | ------------------------------------------------------------- |
| include_z_M     | boolean | 否   | 是否包含模型能力向量z_M，默认true（详情接口默认返回完整信息） |
| include_heatmap | boolean | 否   | 是否包含2D heatmap数据，默认false                             |

**响应参数**

| 参数名                           | 类型    | 说明                                                       |
| -------------------------------- | ------- | ---------------------------------------------------------- |
| success                          | boolean | 请求是否成功                                               |
| message                          | string  | 响应消息                                                   |
| data                             | object  | 模型详细信息                                               |
| data.model_id                    | string  | 模型ID                                                     |
| data.model_name                  | string  | 模型名称                                                   |
| data.model_description           | string  | 模型描述                                                   |
| data.model_provider              | string  | 模型提供商                                                 |
| data.z_M                         | array   | 模型能力向量（1D，仅当include_z_M=true时返回）             |
| data.z_M_dim                     | integer | 能力向量维度（仅当include_z_M=true时返回）                 |
| data.z_M_heatmap                 | array   | 能力向量2D heatmap（可选，仅当include_heatmap=true时返回） |
| data.metadata                    | object  | 模型元数据                                                 |
| data.metadata.cost_per_1k_tokens | float   | 每1000个token的成本                                        |
| data.metadata.latency_p50_ms     | integer | 50分位延迟（毫秒）                                         |
| data.metadata.safety_rating      | integer | 安全性评级                                                 |
| data.metadata.max_context_length | integer | 最大上下文长度                                             |
| data.probe_scores                | array   | 探测集分数（可选）                                         |
| data.probe_scores[].task_type    | string  | 任务类型                                                   |
| data.probe_scores[].score        | float   | 得分                                                       |

**成功响应示例** (200 OK)

```json
{
  "success": true,
  "message": "获取模型详情成功",
  "data": {
    "model_id": "model_abc123",
    "model_name": "gpt-4-turbo",
    "model_description": "OpenAI GPT-4 Turbo model",
    "model_provider": "OpenAI",
    "z_M": [0.12, -0.34, 0.56, 0.78, ...],
    "z_M_dim": 128,
    "z_M_heatmap": [
      [0.1, 0.2, 0.3, ...],
      [0.4, 0.5, 0.6, ...],
      ...
    ],
    "metadata": {
      "cost_per_1k_tokens": 0.01,
      "latency_p50_ms": 500,
      "safety_rating": 5,
      "max_context_length": 128000
    },
    "probe_scores": [
      {"task_type": "chat", "score": 0.95},
      {"task_type": "code", "score": 0.92},
      {"task_type": "math", "score": 0.88}
    ]
  }
}
```

**错误响应示例** (404 Not Found)

```json
{
  "success": false,
  "message": "模型不存在或不可用",
  "error_code": "ROUTER_004",
  "data": null
}
```

---

### 3.5 核心路由接口（Step 3：模型匹配与排序）

**接口描述**：核心路由计算接口。基于QVector和候选模型的能力向量进行匹配，应用权重策略计算最终得分，返回排序后的路由结果。

**⚠️ 重要约束**：

- 该接口是纯计算接口，不生成embedding，不修改模型
- 必须使用已生成的QVector（来自Step 2）
- 权重是策略参数，不持久化

**请求信息**

- **URL**: `/api/v1/router/route`
- **方法**: `POST`
- **Content-Type**: `application/json`
- **Headers**:
  - `Authorization: Bearer {token}`

**请求参数**

| 参数名                          | 类型    | 必填 | 说明                                                                                    |
| ------------------------------- | ------- | ---- | --------------------------------------------------------------------------------------- |
| q_vector                        | array   | 是   | QVector（来自Step 2，固定维度）                                                         |
| candidate_model_ids             | array   | 是   | 候选模型ID数组（至少1个）                                                               |
| weight_config                   | object  | 是   | 权重配置对象                                                                            |
| weight_config.capability_weight | float   | 是   | 能力匹配权重（0.0-1.0）                                                                 |
| weight_config.cost_weight       | float   | 是   | 成本权重（0.0-1.0）                                                                     |
| weight_config.latency_weight    | float   | 是   | 延迟权重（0.0-1.0）                                                                     |
| weight_config.preset            | string  | 否   | 预设策略：`default`, `cost_priority`, `latency_priority`, `capability_priority` |
| include_breakdown               | boolean | 否   | 是否包含得分分解，默认true                                                              |

**权重配置说明**：

- 三个权重之和不需要等于1.0，系统会自动归一化
- 如果提供 `preset`，会覆盖手动设置的权重值
- 预设策略：
  - `default`: capability=0.6, cost=0.2, latency=0.2
  - `cost_priority`: capability=0.4, cost=0.5, latency=0.1
  - `latency_priority`: capability=0.4, cost=0.1, latency=0.5
  - `capability_priority`: capability=0.8, cost=0.1, latency=0.1

**请求示例**

```json
{
  "q_vector": [0.12, -0.34, 0.56, 0.78, ...],
  "candidate_model_ids": ["model_abc123", "model_def456", "model_ghi789"],
  "weight_config": {
    "preset": "default"
  },
  "include_breakdown": true
}
```

或手动设置权重：

```json
{
  "q_vector": [0.12, -0.34, 0.56, 0.78, ...],
  "candidate_model_ids": ["model_abc123", "model_def456"],
  "weight_config": {
    "capability_weight": 0.7,
    "cost_weight": 0.2,
    "latency_weight": 0.1
  },
  "include_breakdown": true
}
```

**响应参数**

| 参数名                                                         | 类型    | 说明                                      |
| -------------------------------------------------------------- | ------- | ----------------------------------------- |
| success                                                        | boolean | 请求是否成功                              |
| message                                                        | string  | 响应消息                                  |
| data                                                           | object  | 响应数据                                  |
| data.routing_results                                           | array   | 路由结果列表（按final_score降序）         |
| data.routing_results[].model_id                                | string  | 模型ID                                    |
| data.routing_results[].model_name                              | string  | 模型名称                                  |
| data.routing_results[].rank                                    | integer | 排名（从1开始）                           |
| data.routing_results[].match_score                             | float   | Match Score（Query-Model相似度，0.0-1.0） |
| data.routing_results[].final_score                             | float   | Final Score（加权后的最终得分）           |
| data.routing_results[].cost                                    | float   | 模型成本（每1k tokens）                   |
| data.routing_results[].latency                                 | integer | 模型延迟（毫秒）                          |
| data.routing_results[].score_breakdown                         | object  | 得分分解（可选）                          |
| data.routing_results[].score_breakdown.capability_contribution | float   | 能力匹配贡献                              |
| data.routing_results[].score_breakdown.cost_penalty            | float   | 成本惩罚                                  |
| data.routing_results[].score_breakdown.latency_penalty         | float   | 延迟惩罚                                  |
| data.weight_config_used                                        | object  | 实际使用的权重配置（归一化后）            |
| data.primary_model                                             | object  | 主推荐模型（Top-1，简化信息）             |
| data.fallback_model                                            | object  | 备用模型（Top-2，简化信息）               |

**成功响应示例** (200 OK)

```json
{
  "success": true,
  "message": "路由计算成功",
  "data": {
    "routing_results": [
      {
        "model_id": "model_abc123",
        "model_name": "gpt-4-turbo",
        "rank": 1,
        "match_score": 0.92,
        "final_score": 0.856,
        "cost": 0.01,
        "latency": 500,
        "score_breakdown": {
          "capability_contribution": 0.552,
          "cost_penalty": -0.002,
          "latency_penalty": -0.100
        }
      },
      {
        "model_id": "model_def456",
        "model_name": "claude-3-opus",
        "rank": 2,
        "match_score": 0.88,
        "final_score": 0.812,
        "cost": 0.015,
        "latency": 600,
        "score_breakdown": {
          "capability_contribution": 0.528,
          "cost_penalty": -0.003,
          "latency_penalty": -0.120
        }
      },
      {
        "model_id": "model_ghi789",
        "model_name": "llama-3-70b",
        "rank": 3,
        "match_score": 0.85,
        "final_score": 0.798,
        "cost": 0.0007,
        "latency": 800,
        "score_breakdown": {
          "capability_contribution": 0.510,
          "cost_penalty": -0.00014,
          "latency_penalty": -0.160
        }
      }
    ],
    "weight_config_used": {
      "capability_weight": 0.6,
      "cost_weight": 0.2,
      "latency_weight": 0.2
    },
    "primary_model": {
      "model_id": "model_abc123",
      "model_name": "gpt-4-turbo",
      "final_score": 0.856
    },
    "fallback_model": {
      "model_id": "model_def456",
      "model_name": "claude-3-opus",
      "final_score": 0.812
    }
  }
}
```

**错误响应示例** (400 Bad Request)

```json
{
  "success": false,
  "message": "QVector维度不匹配",
  "error_code": "ROUTER_005",
  "data": null
}
```

**计算逻辑说明**：

1. **Match Score计算**：

   ```
   match_score = cosine_similarity(q_vector, z_M)
   或
   match_score = dot_product(q_vector, z_M) / (||q_vector|| * ||z_M||)
   ```

   - 结果范围：`[-1, 1]`，通常为 `[0, 1]`（非负相似度）
   - 维度要求：q_vector和z_M必须维度一致（128维）
2. **成本与延迟归一化**：

   **成本归一化**（`normalize_cost`）：

   ```
   normalized_cost = cost / max_cost
   其中 max_cost = 0.1 美元/1k tokens（系统级上限）

   归一化范围：[0, 1]
   - cost = 0.01 → normalized_cost = 0.1
   - cost = 0.05 → normalized_cost = 0.5
   - cost >= 0.1 → normalized_cost = 1.0
   ```

   **延迟归一化**（`normalize_latency`）：

   ```
   normalized_latency = latency / max_latency
   其中 max_latency = 2000 毫秒（系统级上限）

   归一化范围：[0, 1]
   - latency = 500ms → normalized_latency = 0.25
   - latency = 1000ms → normalized_latency = 0.5
   - latency >= 2000ms → normalized_latency = 1.0
   ```

   **重要说明**：

   - 归一化区间为系统级常量，确保不同模型间的公平比较
   - 超出上限的值会被截断为1.0
   - 未来版本可能支持动态调整上限值
3. **Final Score计算**：

   ```
   normalized_weights = normalize([capability_weight, cost_weight, latency_weight])
   其中 normalize 为 L1 归一化：weights / sum(weights)

   capability_contribution = match_score * normalized_weights[0]
   cost_penalty = -normalize_cost(cost) * normalized_weights[1]
   latency_penalty = -normalize_latency(latency) * normalized_weights[2]

   final_score = capability_contribution + cost_penalty + latency_penalty
   ```

   **计算示例**：

   - 假设：match_score=0.92, cost=0.01, latency=500ms
   - 权重配置：capability=0.6, cost=0.2, latency=0.2（已归一化）
   - 计算过程：
     ```
     normalized_cost = 0.01 / 0.1 = 0.1
     normalized_latency = 500 / 2000 = 0.25

     capability_contribution = 0.92 * 0.6 = 0.552
     cost_penalty = -0.1 * 0.2 = -0.02
     latency_penalty = -0.25 * 0.2 = -0.05

     final_score = 0.552 - 0.02 - 0.05 = 0.482
     ```
4. **排序**：按 `final_score`降序排列

---

### 3.6 路由错误码说明

| 错误码     | HTTP状态码 | 说明                                 |
| ---------- | ---------- | ------------------------------------ |
| ROUTER_001 | 400        | 查询文本不能为空                     |
| ROUTER_002 | 400        | embedding_vector格式错误或维度不匹配 |
| ROUTER_003 | 401        | 未授权访问                           |
| ROUTER_004 | 404        | 模型不存在或不可用                   |
| ROUTER_005 | 400        | QVector维度不匹配                    |
| ROUTER_006 | 400        | 候选模型列表为空                     |
| ROUTER_007 | 400        | 权重配置无效（权重为负数或全为0）    |
| ROUTER_008 | 400        | QVector未提供或格式错误              |
| ROUTER_009 | 500        | 路由计算失败（服务器内部错误）       |
| ROUTER_010 | 429        | 请求频率过高                         |

---

### 3.7 路由接口使用流程

**推荐的三步流程**：

1. **Step 1: Embed**

   - 调用 `/api/v1/router/embed`
   - 获取展示用embedding向量
   - 用于UI展示和可解释性分析
2. **Step 2: Encode**

   - 调用 `/api/v1/router/encode`
   - 必须提供 `query_text`（必填）
   - 可选提供 `embedding_vector`（如果已调用Step 1，可传入以提升性能）
   - 获取QVector（匹配向量）
   - **重要**：缓存QVector，避免重复计算
3. **Step 3: Route**

   - 调用 `/api/v1/router/route`
   - 使用Step 2的QVector
   - 选择候选模型和权重配置
   - 获取排序后的路由结果

**优化建议**：

- 如果用户只修改权重配置，只需重新调用Step 3
- 如果用户修改查询文本，需要重新执行Step 1和Step 2
- 模型列表可以预先加载并缓存

---

### 3.8 路由接口设计约束总结

✅ **已遵守的约束**：

1. **Query表征与Model表征严格解耦**

   - QVector通过 `/api/v1/router/encode`生成
   - z_M通过 `/api/v1/admin/models`管理
   - 两者独立，互不干扰
2. **Route接口不得生成embedding**

   - Route接口只接受已生成的QVector
   - 不包含embedding生成逻辑
3. **Route接口不得修改模型**

   - Route接口是纯计算接口
   - 只读操作，无副作用
4. **权重是策略参数，不持久化**

   - 权重配置作为请求参数传递
   - 不存储在数据库中
5. **所有路由结果可解释、可复现**

   - 返回详细的score_breakdown
   - 包含match_score、final_score等可解释指标
   - 相同输入产生相同输出

---

## 4. 通用说明

### 4.1 基础URL

```
开发环境: http://localhost:8000
生产环境: https://api.example.com
```

### 4.2 认证方式

所有需要认证的接口都需要在请求头中携带JWT令牌：

```
Authorization: Bearer {token}
```

### 4.3 统一响应格式

所有接口的响应都遵循以下格式：

**成功响应**

```json
{
  "success": true,
  "message": "操作成功",
  "data": { ... }
}
```

**错误响应**

```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "data": null
}
```

### 4.4 HTTP状态码

| 状态码 | 说明                      |
| ------ | ------------------------- |
| 200    | 请求成功                  |
| 201    | 创建成功                  |
| 400    | 请求参数错误              |
| 401    | 未授权（token无效或缺失） |
| 403    | 权限不足                  |
| 404    | 资源不存在                |
| 429    | 请求频率过高              |
| 500    | 服务器内部错误            |

### 4.5 时间格式

所有时间字段使用ISO 8601格式：

```
2024-01-20T15:30:00Z
```

### 4.6 分页说明

列表接口支持分页，使用 `limit` 和 `offset` 参数：

- `limit`: 每页数量（默认20，最大100）
- `offset`: 偏移量（默认0）

### 4.7 权限说明

- **普通用户** (`role: "user"`): 只能访问用户登录相关接口和路由查询接口
- **管理员** (`role: "admin"`): 可以访问所有接口，包括管理员接口

### 4.8 错误处理

客户端应该根据 `error_code` 进行相应的错误处理。常见错误码：

- `AUTH_*`: 认证相关错误
- `ADMIN_*`: 管理员操作相关错误
- `ROUTER_*`: 路由相关错误（页面3接口）

### 4.9 系统级常量

**向量维度**：

- `QVector维度 = z_M维度 = 128`（系统级常量，不可配置）
- 所有QVector和z_M向量必须严格遵循此维度
- 维度不匹配将导致路由计算失败，返回错误码 `ROUTER_005`

**向量空间约束**：

- QVector和z_M位于同一能力空间（Z-space）
- 两者维度必须完全一致才能进行相似度计算
- 系统会在路由计算前自动校验维度一致性

### 4.10 租户ID（tenant_id）作用范围

`tenant_id` 在路由相关接口中的统一作用：

1. **租户偏好配置**（`/api/v1/router/encode`）：

   - 用于获取租户的默认约束偏好（成本优先/延迟优先/质量优先）
   - 影响可解释特征的生成
   - 可选参数，不提供时使用系统默认值
2. **模型可用性筛选**（`/api/v1/router/models`）：

   - 筛选该租户可访问的模型列表
   - 基于模型的 `tenant_availability` 元数据
   - 可选参数，不提供时返回所有active模型
3. **成本与延迟约束**（未来扩展）：

   - 可用于应用租户级别的成本上限和延迟上限
   - 作为硬约束过滤候选模型

**重要说明**：

- `tenant_id` 不是必填参数，系统支持匿名用户使用默认配置
- 租户配置不影响QVector和z_M的生成，只影响路由策略

### 4.11 Query Embedding 与 QVector 生命周期规则

**缓存与生命周期约束**：

1. **Query Embedding（Step 1）**：

   - 用途：UI展示和可解释性分析
   - 生命周期：与查询文本绑定
   - 缓存规则：查询文本变化时必须重新生成
   - 可缓存：同一查询文本可复用embedding
2. **QVector（Step 2）**：

   - 用途：路由计算的唯一Query表示
   - 生命周期：与查询文本和租户配置绑定
   - 缓存规则：
     - **可复用场景**：查询文本和tenant_id均未变化
     - **必须重新生成场景**：查询文本变化或tenant_id变化
   - **重要**：QVector是路由计算的输入，必须保证一致性
3. **路由结果（Step 3）**：

   - 用途：模型匹配和排序
   - 生命周期：与QVector、候选模型列表、权重配置绑定
   - 缓存规则：
     - **可复用场景**：仅权重配置变化（QVector和模型列表不变）
     - **必须重新计算场景**：QVector变化、模型列表变化、权重配置变化

**最佳实践**：

- 客户端应缓存QVector，避免重复调用 `/api/v1/router/encode`
- 如果用户仅调整权重滑块，只需重新调用 `/api/v1/router/route`
- 如果用户修改查询文本，必须重新执行Step 1和Step 2
- 模型列表建议预先加载并缓存，减少重复请求

---
