package main

import (
	"embed"
	"fmt"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"sync"
)

//go:embed resources/windows/pywin/*
var pyappFS embed.FS

var pythonCacheDir string
var cacheMutex sync.Mutex

func main() {
	pythonDir, err := getPythonRuntime()
	if err != nil {
		panic(err)
	}

	// 调用 Python 脚本
	output, err := runPythonScript(pythonDir, "script.py", "hello")
	if err != nil {
		fmt.Printf("Python error: %v\n%s", err, output)
		return
	}
	fmt.Println("Python output:", string(output))
}

// 获取 Python 运行时（带缓存）
func getPythonRuntime() (string, error) {
	cacheMutex.Lock()
	defer cacheMutex.Unlock()

	if pythonCacheDir != "" {
		// 检查缓存目录是否仍然存在
		if _, err := os.Stat(pythonCacheDir); err == nil {
			return pythonCacheDir, nil
		}
		pythonCacheDir = "" // 缓存失效
	}

	pythonDir, err := extractPythonRuntime()
	if err != nil {
		return "", err
	}

	// 设置缓存（不自动清理）
	pythonCacheDir = pythonDir
	return pythonDir, nil
}

func extractPythonRuntime() (string, error) {
	tmpDir, err := os.MkdirTemp("", "myapp-python-*")
	if err != nil {
		return "", err
	}
	if err := copyFS(tmpDir, pyappFS); err != nil {
		os.RemoveAll(tmpDir)
		return "", err
	}
	// 为解释器添加可执行权限（Linux/macOS）
	if runtime.GOOS != "windows" {
		pythonBin := filepath.Join(tmpDir, "python")
		if err := os.Chmod(pythonBin, 0755); err != nil {
			return "", err
		}
	}
	return tmpDir, nil
}

func copyFS(destDir string, srcFS embed.FS) error {
	return fs.WalkDir(srcFS, ".", func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		// 从完整路径中提取文件名（去掉 resources/windows/pywin/ 前缀）
		basePath := path
		if len(path) > len("resources/windows/pywin/") && path[:len("resources/windows/pywin/")] == "resources/windows/pywin/" {
			basePath = path[len("resources/windows/pywin/"):]
		}
		destPath := filepath.Join(destDir, basePath)
		if d.IsDir() {
			return os.MkdirAll(destPath, 0755)
		}
		data, err := srcFS.ReadFile(path)
		if err != nil {
			return err
		}
		return os.WriteFile(destPath, data, 0644)
	})
}

func runPythonScript(pythonDir, script string, args ...string) ([]byte, error) {
	pythonBin := filepath.Join(pythonDir, "python.exe")
	cmdArgs := append([]string{script}, args...)
	cmd := exec.Command(pythonBin, cmdArgs...)
	cmd.Env = append(os.Environ(),
		"PYTHONHOME="+pythonDir,
		"PYTHONPATH=", // 清空外部 PYTHONPATH
	)
	return cmd.CombinedOutput()
}
