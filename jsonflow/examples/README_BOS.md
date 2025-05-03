# JSONFlow BOS工具

JSONFlow的百度对象存储(BOS)工具提供了一个简单、高效的方式来上传和下载文件。本工具支持单文件操作和目录批量操作，并且内置并发处理功能，可以显著提高大量文件的传输效率。

## 安装依赖

使用此功能需要先安装百度云存储SDK：

```bash
pip install bce-python-sdk
```

或者通过jsonflow的extras依赖安装：

```bash
pip install jsonflow[bos]
```

## 配置认证信息

BOS工具支持两种方式提供认证信息：

1. 通过环境变量：
   ```bash
   export BOS_ACCESS_KEY="你的访问密钥ID"
   export BOS_SECRET_KEY="你的访问密钥Secret"
   export BOS_HOST="bj.bcebos.com"  # 可选，默认为北京区域
   export BOS_BUCKET="你的存储桶名称"  # 可选
   ```

2. 通过API参数直接提供：
   ```python
   from jsonflow.utils.bos import BosHelper
   
   helper = BosHelper(
       access_key_id="你的访问密钥ID",
       secret_access_key="你的访问密钥Secret", 
       endpoint="bj.bcebos.com",
       bucket="你的存储桶名称"
   )
   ```

## 简单使用示例

### 上传单个文件

```python
from jsonflow.utils.bos import upload_file

success, remote_url = upload_file(
    local_file="path/to/local/file.txt",
    remote_key="path/in/bos/file.txt",
    bucket="your-bucket-name",
    access_key_id="your-access-key",  # 可选，如果已设置环境变量
    secret_access_key="your-secret-key"  # 可选，如果已设置环境变量
)

if success:
    print(f"文件已上传: {remote_url}")
else:
    print("上传失败")
```

### 下载单个文件

```python
from jsonflow.utils.bos import download_file

success = download_file(
    remote_key="path/in/bos/file.txt",
    local_file="path/to/save/file.txt",
    bucket="your-bucket-name"
)

if success:
    print("文件已下载")
else:
    print("下载失败")
```

### 并发上传整个目录

```python
from jsonflow.utils.bos import upload_directory

uploaded_urls, failed_files = upload_directory(
    local_dir="path/to/local/directory",
    remote_base_path="path/in/bos",
    bucket="your-bucket-name",
    max_workers=10  # 设置并发工作线程数
)

print(f"已上传 {len(uploaded_urls)} 个文件, 失败 {len(failed_files)} 个文件")
```

### 并发下载前缀下的所有文件

```python
from jsonflow.utils.bos import download_directory

downloaded_files, failed_keys = download_directory(
    remote_prefix="path/in/bos",
    local_dir="path/to/save/directory",
    bucket="your-bucket-name",
    max_workers=10  # 设置并发工作线程数
)

print(f"已下载 {len(downloaded_files)} 个文件, 失败 {len(failed_keys)} 个文件")
```

## 与JSONFlow集成使用

您可以轻松地将BOS文件操作集成到JSONFlow的处理管道中：

```python
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import JsonTransformer
from jsonflow.utils.bos import BosHelper

# 创建BOS辅助工具
bos_helper = BosHelper(bucket="your-bucket-name")

# 定义上传文件的转换操作符
upload_operator = JsonTransformer(lambda data: {
    **data,
    "uploaded": bos_helper.upload_file(
        data.get("local_path", ""), 
        data.get("remote_key", "")
    )[0],
    "remote_url": bos_helper.upload_file(
        data.get("local_path", ""), 
        data.get("remote_key", "")
    )[1]
})

# 创建处理管道
pipeline = Pipeline([
    # 预处理操作符
    JsonTransformer(lambda data: {
        **data,
        "local_path": f"files/{data.get('filename', '')}",
        "remote_key": f"uploads/{data.get('filename', '')}"
    }),
    # 上传操作符
    upload_operator,
    # 其他处理操作符...
])

# 处理JSON数据
json_loader = JsonLoader("input.jsonl")
json_saver = JsonSaver("output.jsonl")

for json_item in json_loader:
    result = pipeline.process(json_item)
    json_saver.write(result)
```

## 命令行使用示例

JSONFlow提供了一个示例脚本，可以从命令行上传和下载文件：

```bash
# 上传示例
python -m jsonflow.examples.bos_example upload \
    --json-file files_to_upload.jsonl \
    --local-dir ./files \
    --remote-path uploads/project \
    --bucket your-bucket-name

# 下载示例
python -m jsonflow.examples.bos_example download \
    --remote-prefix downloads/project \
    --local-dir ./downloaded_files \
    --bucket your-bucket-name \
    --output-file download_results.jsonl
```

## 进阶功能

### BosHelper类

`BosHelper`类提供了更多高级功能：

```python
from jsonflow.utils.bos import BosHelper

# 创建实例
helper = BosHelper(
    bucket="your-bucket-name",
    max_workers=10
)

# 检查存储桶是否存在
if not helper.check_bucket_exists():
    # 创建存储桶
    helper.create_bucket()

# 上传目录
uploaded_urls, failed_files = helper.upload_directory(
    local_dir="path/to/local/directory",
    remote_base_path="path/in/bos"
)

# 下载目录
downloaded_files, failed_keys = helper.download_directory(
    remote_prefix="path/in/bos",
    local_dir="path/to/save/directory"
)
```

## 异常处理

BOS工具对所有操作进行了异常处理，确保不会因为网络问题或权限问题而导致程序崩溃。所有方法都会返回成功/失败状态，让您的应用能够优雅地处理错误情况。 