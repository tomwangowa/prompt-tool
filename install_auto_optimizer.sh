#!/bin/bash

# 🚀 Claude Code自動提示優化器安裝腳本

echo "🚀 Claude Code自動提示優化器安裝程序"
echo "============================================"

# 檢查Python環境
echo "📋 檢查Python環境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 錯誤：需要Python 3.8+，請先安裝Python"
    exit 1
fi

python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
echo "✅ Python版本: $python_version"

# 檢查必要的包
echo "📦 檢查依賴包..."
pip3 install pyperclip flask flask-cors > /dev/null 2>&1
echo "✅ 依賴包安裝完成"

# 設置執行權限
echo "🔐 設置執行權限..."
chmod +x claude_code_hook.py
chmod +x quick_optimize.py
echo "✅ 權限設置完成"

# 創建別名
echo "⚙️  設置命令別名..."
current_dir=$(pwd)

# 檢測shell類型
if [[ $SHELL == *"zsh"* ]]; then
    shell_config="$HOME/.zshrc"
elif [[ $SHELL == *"bash"* ]]; then
    shell_config="$HOME/.bashrc"
else
    shell_config="$HOME/.profile"
fi

# 添加別名到shell配置
cat >> "$shell_config" << EOF

# Claude提示優化器別名
alias opt='python3 $current_dir/quick_optimize.py'
alias optc='python3 $current_dir/quick_optimize.py --copy'
alias opte='python3 $current_dir/quick_optimize.py --show-analysis'

EOF

echo "✅ 別名已添加到 $shell_config"

# 創建Claude Code配置目錄（如果不存在）
claude_config_dir="$HOME/.claude"
if [ ! -d "$claude_config_dir" ]; then
    mkdir -p "$claude_config_dir"
    echo "📁 創建Claude配置目錄: $claude_config_dir"
fi

# 複製設置文件
cp claude_settings.json "$claude_config_dir/settings.json"
echo "⚙️  配置文件已複製到Claude目錄"

# 測試安裝
echo "🧪 測試安裝..."
test_result=$(python3 quick_optimize.py "測試提示" --quiet 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ 安裝測試成功"
else
    echo "⚠️  安裝測試失敗，請檢查AWS憑證配置"
fi

echo ""
echo "🎉 安裝完成！"
echo "============================================"
echo ""
echo "📚 使用方法："
echo "  • 一鍵優化：opt \"你的提示\""
echo "  • 複製優化：optc \"你的提示\""
echo "  • 詳細分析：opte \"你的提示\""
echo ""
echo "🔧 啟動API服務："
echo "  python3 browser_extension_api.py"
echo ""
echo "⚙️  配置文件位置："
echo "  $claude_config_dir/settings.json"
echo ""
echo "📖 詳細文檔："
echo "  查看 AUTO_OPTIMIZATION_GUIDE.md"
echo ""
echo "🔄 重新加載shell配置："
echo "  source $shell_config"
echo ""
echo "⚠️  注意：請確保已配置AWS憑證"
echo "  export AWS_ACCESS_KEY_ID=\"your_key\""
echo "  export AWS_SECRET_ACCESS_KEY=\"your_secret\""
echo ""