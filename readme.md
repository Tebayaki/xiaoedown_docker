该fork将源仓库封装为Docker镜像，修改了部分代码，支持转码为自定义格式。使用方法：
```bash
URL='https://xxx.m3u8'
docker run --rm -it -v ./course:/app/output xiaoedown -u $URL -n lesson1.mp4
```
# XiaoEDown

XiaoEDown 是一个用于下载和合并小鹅通平台 M3U8 视频文件的工具。它支持加密和非加密的 M3U8 流，并使用 FFmpeg 将下载的片段合并为单个视频文件。

## 功能特点

- 支持下载加密和非加密的 M3U8 视频流
- 多线程并发下载，提高下载速度
- 自动解密受保护的内容
- 使用 FFmpeg 合并视频片段
- 简单的命令行界面

## 安装方法

### 使用 pip 安装

```bash
pip install -r requirements.txt
```

### 使用 Conda 安装

```bash
conda create -n xiaoedown python=3.9
conda activate xiaoedown
pip install -r requirements.txt
```

## 依赖项

- Python 3.6+
- FFmpeg (需要在系统路径中)
- 以下 Python 包:
  - requests
  - pycryptodome

## 使用方法

```bash
python main.py -u "M3U8_URL" -n "输出文件名"
```

### 参数说明

- `-u`, `--url`: M3U8 视频流的 URL (必需)
- `-n`, `--name`: 输出视频文件的名称 (可选，默认为 "merge")

### 示例

```bash
python main.py -u "https://example.com/video/main.m3u8" -n "我的视频"
```

## 工作原理

1. 下载 M3U8 文件
2. 解析 M3U8 文件以获取加密密钥(如果有)和 TS 片段 URL
3. 并发下载并解密所有 TS 片段
4. 使用 FFmpeg 将所有片段合并为单个视频文件
5. 清理临时文件

## 注意事项

- 确保 FFmpeg 已安装并添加到系统路径中
- 下载的视频仅供个人学习使用，请尊重版权

## 致谢
感谢 https://github.com/nemoTyrant/goose 项目提供思路