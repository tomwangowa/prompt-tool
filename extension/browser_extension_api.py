#!/usr/bin/env python3
"""
瀏覽器插件API服務
為瀏覽器插件提供提示優化API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from prompt_eval import PromptEvaluator

app = Flask(__name__)
CORS(app)  # 允許跨域請求

# 全局評估器實例
evaluator = PromptEvaluator(llm_type="claude", region="us-west-2")

@app.route('/optimize', methods=['POST'])
def optimize_prompt_api():
    """提示優化API端點"""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'error': '缺少必要的prompt參數',
                'success': False
            }), 400
        
        prompt = data['prompt']
        language = data.get('language', 'zh_TW')
        auto_mode = data.get('auto_mode', True)
        
        # 檢查是否需要優化
        if auto_mode and len(prompt.strip()) < 20:
            return jsonify({
                'optimized_prompt': prompt,
                'is_optimized': False,
                'reason': '提示過短，無需優化',
                'success': True
            })
        
        # 分析提示
        analysis = evaluator.analyze_prompt(prompt, language)
        
        # 計算平均分數
        avg_score = (
            analysis.get("completeness_score", 0) + 
            analysis.get("clarity_score", 0) + 
            analysis.get("structure_score", 0) + 
            analysis.get("specificity_score", 0)
        ) / 4
        
        # 如果分數已經很高，不需要優化
        if auto_mode and avg_score >= 8:
            return jsonify({
                'optimized_prompt': prompt,
                'is_optimized': False,
                'reason': '提示質量已經很高',
                'analysis': analysis,
                'success': True
            })
        
        # 生成默認回答
        default_responses = _generate_default_responses(analysis, language)
        
        # 優化提示
        result = evaluator.optimize_prompt(prompt, default_responses, analysis, language)
        
        return jsonify({
            'optimized_prompt': result.get('enhanced_prompt', prompt),
            'is_optimized': True,
            'original_prompt': prompt,
            'analysis': analysis,
            'improvements': result.get('improvements', []),
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': f'優化失敗: {str(e)}',
            'success': False
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_prompt_api():
    """提示分析API端點"""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'error': '缺少必要的prompt參數',
                'success': False
            }), 400
        
        prompt = data['prompt']
        language = data.get('language', 'zh_TW')
        
        # 分析提示
        analysis = evaluator.analyze_prompt(prompt, language)
        
        return jsonify({
            'analysis': analysis,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': f'分析失敗: {str(e)}',
            'success': False
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'service': 'prompt-optimizer-api',
        'version': '1.0.0'
    })

def _generate_default_responses(analysis: dict, language: str) -> dict:
    """生成默認的用戶回答"""
    responses = {}
    
    # 默認角色設定
    if analysis.get("completeness_score", 0) < 7:
        role_defaults = {
            "zh_TW": "專業助手",
            "en": "professional assistant", 
            "ja": "プロフェッショナルアシスタント"
        }
        responses["role"] = role_defaults.get(language, "專業助手")
    
    # 默認格式設定
    if analysis.get("structure_score", 0) < 6:
        format_defaults = {
            "zh_TW": "結構化列表",
            "en": "structured list",
            "ja": "構造化リスト"
        }
        responses["format"] = format_defaults.get(language, "結構化列表")
    
    # 默認詳細程度
    if analysis.get("specificity_score", 0) < 6:
        detail_defaults = {
            "zh_TW": "詳細說明",
            "en": "detailed explanation",
            "ja": "詳細な説明"
        }
        responses["detail"] = detail_defaults.get(language, "詳細說明")
    
    # 默認推理過程
    if analysis.get("clarity_score", 0) < 7:
        responses["reasoning"] = True
        
    return responses

if __name__ == '__main__':
    print("🚀 提示優化API服務啟動中...")
    print("📡 API端點:")
    print("   POST /optimize - 提示優化")
    print("   POST /analyze  - 提示分析")
    print("   GET  /health   - 健康檢查")
    print("🌐 服務地址: http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
