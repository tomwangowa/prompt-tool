/**
 * Claude Code自動提示優化瀏覽器插件
 * 自動檢測Claude Code輸入框並提供提示優化功能
 */

class ClaudePromptOptimizer {
    constructor() {
        this.apiUrl = 'http://localhost:5000';
        this.enabled = true;
        this.autoOptimize = true;
        this.minPromptLength = 20;
        
        this.init();
    }
    
    init() {
        console.log('🚀 Claude提示優化器已啟動');
        
        // 監聽DOM變化
        this.observeClaudeInterface();
        
        // 添加優化按鈕
        this.addOptimizeButton();
        
        // 添加設置面板
        this.addSettingsPanel();
    }
    
    observeClaudeInterface() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    this.checkForClaudeInput();
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // 初始檢查
        this.checkForClaudeInput();
    }
    
    checkForClaudeInput() {
        // Claude Code輸入框選擇器（需要根據實際情況調整）
        const inputSelectors = [
            'textarea[placeholder*="Message"]',
            'textarea[aria-label*="message"]',
            '.chat-input textarea',
            '[contenteditable="true"]'
        ];
        
        inputSelectors.forEach(selector => {
            const inputs = document.querySelectorAll(selector);
            inputs.forEach(input => {
                if (!input.dataset.optimizerAttached) {
                    this.attachToInput(input);
                    input.dataset.optimizerAttached = 'true';
                }
            });
        });
    }
    
    attachToInput(input) {
        // 添加快捷鍵監聽
        input.addEventListener('keydown', (e) => {
            // Ctrl+Shift+O 優化提示
            if (e.ctrlKey && e.shiftKey && e.key === 'O') {
                e.preventDefault();
                this.optimizeCurrentInput(input);
            }
        });
        
        // 如果啟用自動優化，在輸入時檢查
        if (this.autoOptimize) {
            let timeout;
            input.addEventListener('input', () => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    this.checkAndOptimize(input);
                }, 2000); // 2秒後檢查
            });
        }
    }
    
    async checkAndOptimize(input) {
        const prompt = this.getInputValue(input);
        
        if (prompt.length < this.minPromptLength) {
            return;
        }
        
        // 檢查是否已經是優化過的提示
        if (this.isAlreadyOptimized(prompt)) {
            return;
        }
        
        try {
            const response = await this.analyzePrompt(prompt);
            if (response.success) {
                const avgScore = this.calculateAverageScore(response.analysis);
                if (avgScore < 7) {
                    this.showOptimizationSuggestion(input, prompt);
                }
            }
        } catch (error) {
            console.error('提示分析失敗:', error);
        }
    }
    
    async optimizeCurrentInput(input) {
        const prompt = this.getInputValue(input);
        
        if (!prompt.trim()) {
            this.showNotification('請先輸入提示內容', 'warning');
            return;
        }
        
        this.showLoadingIndicator(input);
        
        try {
            const response = await this.optimizePrompt(prompt);
            
            if (response.success && response.is_optimized) {
                this.setInputValue(input, response.optimized_prompt);
                this.showNotification('提示已優化完成！', 'success');
                
                // 顯示改進詳情
                if (response.improvements) {
                    this.showImprovementDetails(response.improvements);
                }
            } else {
                this.showNotification(response.reason || '提示無需優化', 'info');
            }
        } catch (error) {
            console.error('提示優化失敗:', error);
            this.showNotification('優化失敗，請檢查網絡連接', 'error');
        } finally {
            this.hideLoadingIndicator(input);
        }
    }
    
    async optimizePrompt(prompt, language = 'zh_TW') {
        const response = await fetch(`${this.apiUrl}/optimize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: prompt,
                language: language,
                auto_mode: true
            })
        });
        
        return await response.json();
    }
    
    async analyzePrompt(prompt, language = 'zh_TW') {
        const response = await fetch(`${this.apiUrl}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: prompt,
                language: language
            })
        });
        
        return await response.json();
    }
    
    getInputValue(input) {
        return input.value || input.textContent || input.innerText || '';
    }
    
    setInputValue(input, value) {
        if (input.tagName === 'TEXTAREA' || input.tagName === 'INPUT') {
            input.value = value;
        } else {
            input.textContent = value;
        }
        
        // 觸發input事件
        input.dispatchEvent(new Event('input', { bubbles: true }));
    }
    
    isAlreadyOptimized(prompt) {
        const optimizedIndicators = [
            '你是一個', 'You are a', 'あなたは',
            '請按照以下步驟', 'Please follow these steps',
            '輸出格式：', 'Output format:',
            '## ', '### ', '```'
        ];
        
        return optimizedIndicators.some(indicator => prompt.includes(indicator));
    }
    
    calculateAverageScore(analysis) {
        const scores = [
            analysis.completeness_score || 0,
            analysis.clarity_score || 0,
            analysis.structure_score || 0,
            analysis.specificity_score || 0
        ];
        return scores.reduce((a, b) => a + b, 0) / scores.length;
    }
    
    showOptimizationSuggestion(input, prompt) {
        const suggestion = document.createElement('div');
        suggestion.className = 'claude-optimizer-suggestion';
        suggestion.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: #f0f9ff;
                border: 2px solid #0ea5e9;
                border-radius: 8px;
                padding: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 10000;
                max-width: 300px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            ">
                <div style="font-weight: 600; color: #0369a1; margin-bottom: 8px;">
                    💡 建議優化提示
                </div>
                <div style="font-size: 14px; color: #64748b; margin-bottom: 12px;">
                    您的提示可以進一步優化以獲得更好的回答
                </div>
                <div style="display: flex; gap: 8px;">
                    <button class="optimize-btn" style="
                        background: #0ea5e9;
                        color: white;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                    ">優化</button>
                    <button class="dismiss-btn" style="
                        background: #e2e8f0;
                        color: #64748b;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                    ">忽略</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(suggestion);
        
        // 綁定事件
        suggestion.querySelector('.optimize-btn').onclick = () => {
            this.optimizeCurrentInput(input);
            suggestion.remove();
        };
        
        suggestion.querySelector('.dismiss-btn').onclick = () => {
            suggestion.remove();
        };
        
        // 5秒後自動移除
        setTimeout(() => {
            if (suggestion.parentNode) {
                suggestion.remove();
            }
        }, 5000);
    }
    
    showNotification(message, type = 'info') {
        const colors = {
            success: { bg: '#dcfce7', border: '#16a34a', text: '#15803d' },
            error: { bg: '#fef2f2', border: '#dc2626', text: '#b91c1c' },
            warning: { bg: '#fef3c7', border: '#d97706', text: '#92400e' },
            info: { bg: '#eff6ff', border: '#2563eb', text: '#1d4ed8' }
        };
        
        const color = colors[type] || colors.info;
        
        const notification = document.createElement('div');
        notification.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${color.bg};
                border: 1px solid ${color.border};
                color: ${color.text};
                padding: 12px 16px;
                border-radius: 6px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 10001;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 14px;
                max-width: 300px;
            ">
                ${message}
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
    
    showLoadingIndicator(input) {
        const indicator = document.createElement('div');
        indicator.className = 'claude-optimizer-loading';
        indicator.innerHTML = `
            <div style="
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                z-index: 10002;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            ">
                <div style="margin-bottom: 12px;">⚡ 正在優化提示...</div>
                <div style="font-size: 12px; opacity: 0.8;">請稍候，AI正在分析您的提示</div>
            </div>
        `;
        
        document.body.appendChild(indicator);
    }
    
    hideLoadingIndicator() {
        const indicator = document.querySelector('.claude-optimizer-loading');
        if (indicator) {
            indicator.remove();
        }
    }
    
    addOptimizeButton() {
        // 在頁面添加浮動優化按鈕
        const button = document.createElement('div');
        button.innerHTML = `
            <div id="claude-optimizer-btn" style="
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 56px;
                height: 56px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                z-index: 9999;
                transition: transform 0.2s;
                font-size: 24px;
            " title="優化提示 (Ctrl+Shift+O)">
                ⚡
            </div>
        `;
        
        document.body.appendChild(button);
        
        const btn = document.getElementById('claude-optimizer-btn');
        btn.onclick = () => {
            const activeInput = document.activeElement;
            if (activeInput && (activeInput.tagName === 'TEXTAREA' || activeInput.tagName === 'INPUT' || activeInput.contentEditable === 'true')) {
                this.optimizeCurrentInput(activeInput);
            } else {
                this.showNotification('請先點擊輸入框', 'warning');
            }
        };
        
        btn.onmouseenter = () => {
            btn.style.transform = 'scale(1.1)';
        };
        
        btn.onmouseleave = () => {
            btn.style.transform = 'scale(1)';
        };
    }
    
    showImprovementDetails(improvements) {
        const details = document.createElement('div');
        details.innerHTML = `
            <div style="
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.12);
                z-index: 10003;
                max-width: 500px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            ">
                <div style="font-size: 18px; font-weight: 600; margin-bottom: 16px; color: #1f2937;">
                    🎯 優化改進詳情
                </div>
                <div style="margin-bottom: 20px;">
                    ${improvements.map(imp => `
                        <div style="
                            padding: 8px 12px;
                            background: #f8fafc;
                            border-left: 3px solid #10b981;
                            margin-bottom: 8px;
                            font-size: 14px;
                            color: #374151;
                        ">
                            ${imp}
                        </div>
                    `).join('')}
                </div>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: #6366f1;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                ">確定</button>
            </div>
        `;
        
        document.body.appendChild(details);
        
        // 3秒後自動關閉
        setTimeout(() => {
            if (details.parentNode) {
                details.remove();
            }
        }, 8000);
    }
}

// 啟動優化器
const claudeOptimizer = new ClaudePromptOptimizer();