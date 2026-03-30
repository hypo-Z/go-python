package main

import (
	"embed"
	"fmt"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
)

// go:embed pyapp
var pyappFS embed.FS

func main() {
	pythonDir, err := extractPythonRuntime()
	if err != nil {
		panic(err)
	}
	defer os.RemoveAll(pythonDir) // 退出时清理

	// 调用 Python 脚本
	output, err := runPythonScript(pythonDir, "script.py", "hello")
	if err != nil {
		fmt.Printf("Python error: %v\n%s", err, output)
		return
	}
	fmt.Println("Python output:", string(output))
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
		destPath := filepath.Join(destDir, path)
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
	pythonBin := filepath.Join(pythonDir, "python")
	if runtime.GOOS == "windows" {
		pythonBin += ".exe"
	}
	cmdArgs := append([]string{script}, args...)
	cmd := exec.Command(pythonBin, cmdArgs...)
	cmd.Env = append(os.Environ(),
		"PYTHONHOME="+pythonDir,
		"PYTHONPATH=", // 清空外部 PYTHONPATH
	)
	return cmd.CombinedOutput()
}
