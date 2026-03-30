import sys
import io

# 设置标准输出的编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 你的业务逻辑
def process(data):
    return f"✅ Python 处理成功：{data} (来自Go)"

if __name__ == "__main__":
    # 接收 Go 传的参数
    msg = sys.argv[1] if len(sys.argv) > 1 else "无参数"

    # 处理并输出给 Go
    print(process(msg))