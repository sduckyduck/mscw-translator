# MSCW Translator

冒险岛聊天翻译器：截图 OCR + 冒险岛术语词库 + 本地大语言模型翻译 + 快捷英文回复。

核心原则：

**只读屏幕，不读游戏内存，不注入 DLL，不抓包，不自动打字，不自动玩游戏。**

## 当前功能

- 中文 PyQt6 桌面界面。
- 手动粘贴英文聊天并翻译。
- 框选屏幕区域进行 OCR 识别。
- 默认识别左下角聊天区域。
- 本地冒险岛术语词库。
- 优先使用 Ollama 本地开源大语言模型翻译。
- 可选 DeepL API fallback。
- 快捷英文回复建议。
- 一键复制原文、翻译、第一条回复。

## 本地安装

Windows PowerShell：

```powershell
git clone https://github.com/sduckyduck/mscw-translator.git
cd mscw-translator
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m mscw_translator
```

## 使用本地开源大语言模型翻译，不接外部 API

推荐使用 Ollama。

### 1. 安装 Ollama

去 Ollama 官网安装 Windows 版本。

### 2. 下载并运行模型

推荐先用小模型，速度快：

```powershell
ollama run qwen2.5:3b
```

如果电脑性能更好，可以试：

```powershell
ollama run qwen2.5:7b
```

### 3. 启动翻译器

保持 Ollama 在后台运行，然后：

```powershell
python -m mscw_translator
```

默认模型是：

```text
qwen2.5:3b
```

更换模型：

```powershell
$env:OLLAMA_MODEL="qwen2.5:7b"
python -m mscw_translator
```

## OCR 安装

如果界面显示 OCR 未启用，运行：

```powershell
pip install paddleocr paddlepaddle
```

然后重新启动：

```powershell
python -m mscw_translator
```

如果 OCR 仍然失败，也可以先手动粘贴英文聊天测试翻译。

## 推荐使用流程

1. 游戏设置成窗口化或无边框窗口化。
2. 打开翻译器。
3. 点“框选截图识别”。
4. 用鼠标框选游戏聊天框。
5. 松开鼠标后自动 OCR + 翻译。
6. 查看中文意思和推荐英文回复。
7. 点“复制第一条回复”。
8. 回到游戏里手动粘贴发送。

## 示例

输入：

```text
LF> bishop for cpq
```

程序会结合词库理解：

```text
LF> = 寻找
bishop = 主教
cpq = 嘉年华组队任务
```

并给出类似：

```text
【中文意思】
正在找一个主教一起打 CPQ。

【推荐回复】
Sure, invite me please!
One sec, I can join soon.
Sorry, I cannot right now.
```

## 安全说明

本项目不接触游戏进程，只处理屏幕截图和用户手动输入。这样风险更低，但任何第三方工具都不能保证一定符合所有游戏条款。建议保持“只读屏幕 + 手动复制粘贴”的使用方式。
