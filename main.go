package main

import (
	"bytes"
	"embed"
	"fmt"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
)

// 👇 自动打包 Python 解释器所有文件
// go:embed python311
var pythonFiles embed.FS

// go:embed script.py
var pyScript []byte

func main() {
	// 1. 创建临时目录
	tmp, _ := os.MkdirTemp("", "go-py-")
	defer os.RemoveAll(tmp)

	// 2. 释放 Python 解释器
	copyPythonFiles("python311", tmp)

	// 3. 释放 Python 脚本
	scriptPath := filepath.Join(tmp, "script.py")
	os.WriteFile(scriptPath, pyScript, 0755)

	// 4. 运行 Python 脚本
	var pythonExec string
	if isWindows() {
		pythonExec = filepath.Join(tmp, "python311", "python.exe")
	} else {
		// 检查是否有可执行的python文件
		macPythonExec := filepath.Join(tmp, "python311", "python")
		unixPythonExec := filepath.Join(tmp, "python311", "python3")

		// 如果当前目录下没有合适的python执行文件，则需要提供正确的Python环境
		// 或者回退到系统Python
		if _, err := os.Stat(macPythonExec); err == nil {
			pythonExec = macPythonExec
		} else if _, err := os.Stat(unixPythonExec); err == nil {
			pythonExec = unixPythonExec
		} else {
			// 如果嵌入的Python不适用于当前系统，可以考虑使用系统Python
			systemPython, err := exec.LookPath("python3")
			if err != nil {
				systemPython, err = exec.LookPath("python")
				if err != nil {
					fmt.Println("错误：无法找到Python解释器")
					return
				}
			}
			// 在这种情况下，我们需要单独处理脚本，而不是使用嵌入的Python
			fmt.Printf("警告：未找到嵌入的Python解释器，使用系统Python: %s\n", systemPython)

			cmd := exec.Command(
				systemPython,
				scriptPath,
				"你好Go！", // 传给 Python 的参数
			)

			var out, errOut bytes.Buffer
			cmd.Stdout = &out
			cmd.Stderr = &errOut

			// 执行
			err = cmd.Run()
			if err != nil {
				fmt.Println("Python 错误：", errOut.String())
				panic(err)
			}

			// 5. Go 接收结果
			fmt.Println("Go 收到：", out.String())
			return
		}
	}

	cmd := exec.Command(
		pythonExec,
		scriptPath,
		"你好Go！", // 传给 Python 的参数
	)

	var out, errOut bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &errOut

	// 执行
	err := cmd.Run()
	if err != nil {
		fmt.Println("Python 错误：", errOut.String())
		panic(err)
	}

	// 5. Go 接收结果
	fmt.Println("Go 收到：", out.String())
}

// 复制 Python 解释器文件
func copyPythonFiles(src, dst string) error {
	return fs.WalkDir(pythonFiles, src, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		fullPath := filepath.Join(dst, path)
		if d.IsDir() {
			return os.MkdirAll(fullPath, 0755)
		}
		data, err := pythonFiles.ReadFile(path)
		if err != nil {
			return err
		}
		return os.WriteFile(fullPath, data, 0755)
	})
}

// 判断是否为 Windows 系统
func isWindows() bool {
	return os.PathSeparator == '\\'
}
