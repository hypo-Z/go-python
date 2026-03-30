import sys
import io
import json
import os
import time
import hashlib
import base64
import random
from datetime import datetime
from urllib.request import urlopen
from urllib.error import URLError

# 尝试导入版本获取模块
try:
    import importlib.metadata
    IMPORTLIB_METADATA_AVAILABLE = True
except ImportError:
    # Python < 3.8 兼容
    try:
        import importlib_metadata as importlib_metadata
        IMPORTLIB_METADATA_AVAILABLE = True
    except ImportError:
        IMPORTLIB_METADATA_AVAILABLE = False

# 设置标准输出的编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加自定义模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'site-packages'))

# 尝试导入自定义模块
try:
    from mylib import DataValidator, ConfigManager
except ImportError as e:
    print(f"⚠️ 自定义模块导入警告: {e}")
    # 创建虚拟模块类
    class DataValidator:
        def validate_email(self, email):
            return "@" in email if email else False
        
        def validate_phone(self, phone):
            return phone and phone.replace("-", "").replace(" ", "").isdigit()
    
    class ConfigManager:
        def __init__(self):
            self.config = {"version": "1.0", "environment": "test"}
        
        def get(self, key, default=None):
            return self.config.get(key, default)

# 尝试导入第三方库
try:
    import requests
except ImportError:
    requests = None
    print("⚠️ requests 库不可用，使用内置 urllib")

# 数据处理模块（增强版）
class DataProcessor:
    def __init__(self):
        self.processed_count = 0
    
    def process_data(self, data):
        """复杂的数据处理逻辑（增强版）"""
        # 1. 数据验证
        validator = DataValidator()
        validation_result = {
            "is_empty": not data or len(data.strip()) == 0,
            "is_email": validator.validate_email(data) if "@" in data else False,
            "is_phone": validator.validate_phone(data) if any(c.isdigit() for c in data) else False,
            "has_special_chars": any(not c.isalnum() for c in data) if data else False
        }
        
        if validation_result["is_empty"]:
            return {"error": "输入数据为空", "validation": validation_result}
        
        # 2. 数据转换
        processed = {
            "original": data,
            "length": len(data),
            "upper": data.upper(),
            "lower": data.lower(),
            "words": len(data.split()),
            "hash_md5": hashlib.md5(data.encode()).hexdigest(),
            "hash_sha256": hashlib.sha256(data.encode()).hexdigest(),
            "base64": base64.b64encode(data.encode()).decode(),
            "timestamp": datetime.now().isoformat(),
            "validation": validation_result
        }
        
        # 3. 统计分析
        char_count = {}
        for char in data:
            if char.isalnum():
                char_count[char] = char_count.get(char, 0) + 1
        processed["char_frequency"] = char_count
        
        # 4. 使用配置管理器
        config = ConfigManager()
        processed["config"] = {
            "version": config.get("version"),
            "environment": config.get("environment")
        }
        
        self.processed_count += 1
        processed["process_id"] = self.processed_count
        
        return processed

# 文件操作模块
class FileManager:
    def __init__(self, base_dir="data"):
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
    
    def save_result(self, data, filename=None):
        """保存处理结果到文件"""
        if filename is None:
            filename = f"result_{int(time.time())}_{random.randint(1000, 9999)}.json"
        
        filepath = os.path.join(self.base_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {
            "file_saved": True,
            "filepath": filepath,
            "size": os.path.getsize(filepath)
        }
    
    def list_files(self):
        """列出所有保存的文件"""
        if not os.path.exists(self.base_dir):
            return []
        
        files = []
        for filename in os.listdir(self.base_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.base_dir, filename)
                files.append({
                    "name": filename,
                    "size": os.path.getsize(filepath),
                    "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                })
        
        return files

# 网络请求模块（增强版）
class NetworkService:
    def __init__(self):
        self.timeout = 10
    
    def get_public_ip(self):
        """获取公网IP地址"""
        # 优先使用 requests 库
        if requests:
            try:
                response = requests.get('http://httpbin.org/ip', timeout=self.timeout)
                return {"success": True, "ip": response.json().get('origin'), "library": "requests"}
            except Exception as e:
                return {"success": False, "error": str(e), "library": "requests"}
        
        # 回退到 urllib
        try:
            with urlopen('http://httpbin.org/ip', timeout=self.timeout) as response:
                data = json.loads(response.read().decode())
                return {"success": True, "ip": data.get('origin'), "library": "urllib"}
        except URLError as e:
            return {"success": False, "error": str(e), "library": "urllib"}
    
    def check_internet(self):
        """检查网络连接"""
        # 优先使用 requests 库
        if requests:
            try:
                response = requests.get('http://httpbin.org/get', timeout=self.timeout)
                return {"success": True, "status": response.status_code, "library": "requests"}
            except Exception as e:
                return {"success": False, "error": str(e), "library": "requests"}
        
        # 回退到 urllib
        try:
            with urlopen('http://httpbin.org/get', timeout=self.timeout) as response:
                return {"success": True, "status": response.status, "library": "urllib"}
        except URLError as e:
            return {"success": False, "error": str(e), "library": "urllib"}

# 第三方库测试模块
class ThirdPartyTester:
    def __init__(self):
        self.available_libraries = {}
        self.test_libraries()
    
    def test_libraries(self):
        """测试可用的第三方库"""
        libraries_to_test = [
            ("json", "标准库"),
            ("hashlib", "标准库"),
            ("base64", "标准库"),
            ("requests", "第三方"),
            ("numpy", "第三方"),
            ("pandas", "第三方"),
            ("matplotlib", "第三方")
        ]
        
        for lib_name, lib_type in libraries_to_test:
            try:
                __import__(lib_name)
                self.available_libraries[lib_name] = {
                    "type": lib_type,
                    "available": True,
                    "version": self.get_library_version(lib_name)
                }
            except ImportError:
                self.available_libraries[lib_name] = {
                    "type": lib_type,
                    "available": False,
                    "version": None
                }
    
    def get_library_version(self, lib_name):
        """获取库版本"""
        try:
            if lib_name == "json" or lib_name == "hashlib" or lib_name == "base64":
                return "built-in"
            
            # 如果有 importlib.metadata 或 importlib_metadata，优先使用它
            if IMPORTLIB_METADATA_AVAILABLE:
                try:
                    if 'importlib.metadata' in sys.modules:
                        version = importlib.metadata.version(lib_name)
                    else:
                        version = importlib_metadata.version(lib_name)
                    return version
                except Exception:
                    # 如果 importlib.metadata 获取失败，回退到其他方法
                    pass

            # 回退到原来的方案
            module = __import__(lib_name)
            
            # 尝试 __version__ 属性
            version = getattr(module, "__version__", None)
            if version:
                return str(version)
            
            # 尝试 version 属性
            version = getattr(module, "version", None)
            if version:
                if isinstance(version, tuple):
                    return '.'.join(map(str, version))
                return str(version)
            
            # 尝试 VERSION 属性
            version = getattr(module, "VERSION", None)
            if version:
                if isinstance(version, tuple):
                    return '.'.join(map(str, version))
                return str(version)
            
            # 对于特定库尝试特殊属性
            if lib_name == "requests":
                import requests
                return str(requests.__version__)
            elif lib_name == "numpy":
                import numpy
                return str(numpy.__version__)
            elif lib_name == "pandas":
                import pandas
                return str(pandas.__version__)
            elif lib_name == "matplotlib":
                import matplotlib
                return str(matplotlib.__version__)
            
            return "unknown"
        except Exception as e:
            return "unknown"

# 主业务逻辑（增强版）
class ComplexProcessor:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.file_manager = FileManager()
        self.network_service = NetworkService()
        self.library_tester = ThirdPartyTester()
    
    def process_complex(self, input_data, save_file=True, check_network=True):
        """完整的复杂处理流程"""
        result = {
            "start_time": datetime.now().isoformat(),
            "input": input_data,
            "steps": []
        }
        
        # 步骤1: 数据处理
        step1_start = time.time()
        processed_data = self.data_processor.process_data(input_data)
        step1_time = time.time() - step1_start
        
        result["steps"].append({
            "name": "数据处理",
            "duration": round(step1_time, 4),
            "result": processed_data
        })
        
        # 步骤2: 文件保存（可选）
        if save_file:
            step2_start = time.time()
            file_result = self.file_manager.save_result(processed_data)
            step2_time = time.time() - step2_start
            
            result["steps"].append({
                "name": "文件保存",
                "duration": round(step2_time, 4),
                "result": file_result
            })
        
        # 步骤3: 网络检查（可选）
        if check_network:
            step3_start = time.time()
            network_result = self.network_service.check_internet()
            step3_time = time.time() - step3_start
            
            result["steps"].append({
                "name": "网络检查",
                "duration": round(step3_time, 4),
                "result": network_result
            })
        
        # 步骤4: 列出所有文件
        step4_start = time.time()
        file_list = self.file_manager.list_files()
        step4_time = time.time() - step4_start
        
        result["steps"].append({
            "name": "文件列表",
            "duration": round(step4_time, 4),
            "result": {"file_count": len(file_list), "files": file_list}
        })
        
        # 步骤5: 库可用性测试
        step5_start = time.time()
        library_report = self.library_tester.available_libraries
        step5_time = time.time() - step5_start
        
        result["steps"].append({
            "name": "库可用性测试",
            "duration": round(step5_time, 4),
            "result": library_report
        })
        
        result["end_time"] = datetime.now().isoformat()
        result["total_duration"] = round(time.time() - step1_start, 4)
        result["status"] = "✅ 处理完成"
        
        return result

def main():
    # 接收 Go 传的参数
    msg = sys.argv[1] if len(sys.argv) > 1 else "默认测试数据 Hello World!"
    
    # 可选参数处理
    save_file = "--no-save" not in sys.argv
    check_network = "--no-network" not in sys.argv
    
    # 创建处理器并执行
    processor = ComplexProcessor()
    
    print("🚀 开始复杂处理流程...")
    print(f"输入数据: {msg}")
    print(f"保存文件: {'是' if save_file else '否'}")
    print(f"检查网络: {'是' if check_network else '否'}")
    print("-" * 50)
    
    try:
        result = processor.process_complex(msg, save_file, check_network)
        
        # 输出结果
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "status": "❌ 处理失败"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()