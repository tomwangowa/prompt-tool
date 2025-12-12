#!/usr/bin/env python3
"""
Prompt Loader - YAML-based Prompt Configuration Loader
Loads and manages prompts from external YAML configuration files
"""

import yaml
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptLoader:
    """Loads and manages prompts from YAML configuration files"""
    
    def __init__(self, config_path: str = "resources/prompts/prompts.yaml"):
        """
        Initialize the prompt loader
        
        Args:
            config_path: Path to the prompts YAML file
        """
        self.config_path = Path(config_path)
        self.prompts = {}
        self._load()
    
    def _load(self) -> None:
        """Load prompts from YAML file"""
        try:
            if not self.config_path.exists():
                logger.warning(f"Prompt config file not found: {self.config_path}")
                logger.warning("Using empty configuration")
                self.prompts = self._get_default_config()
                return
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.prompts = yaml.safe_load(f)
            
            logger.info(f"Loaded prompts from {self.config_path}")
            logger.info(f"Version: {self.prompts.get('version', 'unknown')}")
            logger.info(f"Languages: {', '.join(self.prompts.get('languages', []))}")
        
        except Exception as e:
            logger.error(f"Error loading prompts: {e}")
            logger.warning("Falling back to default configuration")
            self.prompts = self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get minimal default configuration as fallback"""
        return {
            "version": "1.0",
            "languages": ["zh_TW", "en", "ja"],
            "system_prompts": {},
            "user_prompts": {},
            "dynamic_questions": {},
            "optimization_strategies": {},
            "improvement_messages": {}
        }
    
    def get_system_prompt(self, prompt_type: str, language: str = "zh_TW") -> str:
        """
        Get system prompt for a specific type and language
        
        Args:
            prompt_type: Type of prompt (e.g., 'analyze', 'optimize')
            language: Language code (e.g., 'zh_TW', 'en', 'ja')
        
        Returns:
            System prompt text
        """
        try:
            return self.prompts['system_prompts'][prompt_type][language]
        except KeyError:
            logger.warning(f"System prompt not found: {prompt_type}/{language}")
            return ""
    
    def get_user_prompt(
        self, 
        prompt_type: str, 
        language: str = "zh_TW", 
        **kwargs
    ) -> str:
        """
        Get user prompt template and render with variables
        
        Args:
            prompt_type: Type of prompt (e.g., 'analyze', 'optimize')
            language: Language code
            **kwargs: Variables to render in the template
        
        Returns:
            Rendered user prompt text
        """
        try:
            prompt_config = self.prompts['user_prompts'][prompt_type]
            template = prompt_config['template']
            
            # Get language-specific content
            render_vars = kwargs.copy()
            
            # Add output_format if exists
            if 'output_format' in prompt_config:
                render_vars['output_format'] = prompt_config['output_format'].get(
                    language, prompt_config['output_format'].get('zh_TW', '')
                )
            
            # Add scoring_criteria if exists
            if 'scoring_criteria' in prompt_config:
                render_vars['scoring_criteria'] = prompt_config['scoring_criteria'].get(
                    language, prompt_config['scoring_criteria'].get('zh_TW', '')
                )
            
            # Add optimization_requirements if exists
            if 'optimization_requirements' in prompt_config:
                render_vars['optimization_requirements'] = prompt_config['optimization_requirements'].get(
                    language, prompt_config['optimization_requirements'].get('zh_TW', '')
                )
            
            # Add output_instructions if exists
            if 'output_instructions' in prompt_config:
                render_vars['output_instructions'] = prompt_config['output_instructions'].get(
                    language, prompt_config['output_instructions'].get('zh_TW', '')
                )
            
            # Render template
            return template.format(**render_vars)
        
        except KeyError as e:
            logger.warning(f"User prompt not found: {prompt_type}/{language} - {e}")
            return ""
        except Exception as e:
            logger.error(f"Error rendering user prompt: {e}")
            return ""
    
    def get_dynamic_questions(
        self, 
        analysis: Dict[str, Any], 
        language: str = "zh_TW"
    ) -> List[Dict[str, str]]:
        """
        Generate dynamic questions based on analysis results
        
        Args:
            analysis: Analysis results dict with scores
            language: Language code
        
        Returns:
            List of questions with type and text
        """
        questions = []
        
        try:
            dynamic_questions = self.prompts.get('dynamic_questions', {})
            
            for q_type, config in dynamic_questions.items():
                condition = config.get('condition', '')
                
                # Evaluate condition
                if self._evaluate_condition(condition, analysis):
                    question_text = config['questions'].get(
                        language, 
                        config['questions'].get('zh_TW', '')
                    )
                    
                    questions.append({
                        "question": question_text,
                        "type": q_type,
                        "priority": config.get('priority', 5)
                    })
            
            # Sort by priority (higher first)
            questions.sort(key=lambda x: x.get('priority', 5), reverse=True)
        
        except Exception as e:
            logger.error(f"Error generating dynamic questions: {e}")
        
        return questions
    
    def _evaluate_condition(self, condition: str, analysis: Dict[str, Any]) -> bool:
        """
        Evaluate a condition expression
        
        Args:
            condition: Condition string (e.g., "completeness_score < 7")
            analysis: Analysis dict with scores
        
        Returns:
            True if condition is met
        """
        try:
            # Simple evaluation for common conditions
            # Security: Only allow simple comparison expressions
            
            # Check for score comparisons
            if '<' in condition:
                parts = condition.split('<')
                if len(parts) == 2:
                    key = parts[0].strip()
                    threshold = float(parts[1].strip())
                    return analysis.get(key, 10) < threshold
            
            # Check for "in" conditions (for complexity_level)
            if ' in ' in condition:
                parts = condition.split(' in ')
                if len(parts) == 2:
                    key = parts[0].strip()
                    # Parse list from string like "['複雜', 'Complex', '複雑']"
                    values_str = parts[1].strip()
                    if values_str.startswith('[') and values_str.endswith(']'):
                        # Simple parsing - extract quoted strings
                        import re
                        values = re.findall(r"'([^']*)'", values_str)
                        return analysis.get(key, '') in values
            
            # Check for "OR" conditions
            if ' OR ' in condition:
                subconditions = condition.split(' OR ')
                return any(self._evaluate_condition(sc.strip(), analysis) for sc in subconditions)
            
            return False
        
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False
    
    def get_optimization_strategy(
        self, 
        strategy_name: str, 
        language: str = "zh_TW",
        **kwargs
    ) -> Optional[str]:
        """
        Get optimization strategy template
        
        Args:
            strategy_name: Strategy name (e.g., 'role_enhancement')
            language: Language code
            **kwargs: Variables to render in the template
        
        Returns:
            Rendered strategy text or None if disabled/not found
        """
        try:
            strategies = self.prompts.get('optimization_strategies', {})
            strategy = strategies.get(strategy_name, {})
            
            if not strategy.get('enabled', False):
                return None
            
            template = strategy['template'].get(
                language,
                strategy['template'].get('zh_TW', '')
            )
            
            return template.format(**kwargs)
        
        except Exception as e:
            logger.error(f"Error getting optimization strategy '{strategy_name}': {e}")
            return None
    
    def get_improvement_message(
        self, 
        message_key: str, 
        language: str = "zh_TW"
    ) -> str:
        """
        Get improvement message text
        
        Args:
            message_key: Message key (e.g., 'role_added', 'final_improvement')
            language: Language code
        
        Returns:
            Message text
        """
        try:
            messages = self.prompts.get('improvement_messages', {})
            message = messages.get(message_key, {})
            return message.get(language, message.get('zh_TW', ''))
        except Exception as e:
            logger.error(f"Error getting improvement message '{message_key}': {e}")
            return ""
    
    def reload(self) -> None:
        """Reload prompts from file (hot reload)"""
        logger.info("Reloading prompts...")
        self._load()
    
    def get_version(self) -> str:
        """Get configuration version"""
        return self.prompts.get('version', 'unknown')
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self.prompts.get('languages', ['zh_TW'])
    
    def validate_config(self) -> bool:
        """
        Validate configuration structure
        
        Returns:
            True if valid, False otherwise
        """
        required_keys = ['version', 'languages', 'system_prompts', 'user_prompts']
        
        for key in required_keys:
            if key not in self.prompts:
                logger.error(f"Missing required key: {key}")
                return False
        
        logger.info("Configuration validation passed")
        return True


# Singleton instance for global access
_default_loader = None


def get_default_loader() -> PromptLoader:
    """Get default singleton prompt loader instance"""
    global _default_loader
    if _default_loader is None:
        _default_loader = PromptLoader()
    return _default_loader


if __name__ == "__main__":
    # Test the loader
    print("Testing PromptLoader...")
    
    loader = PromptLoader()
    
    print(f"\nVersion: {loader.get_version()}")
    print(f"Languages: {loader.get_supported_languages()}")
    print(f"Valid: {loader.validate_config()}")
    
    print("\n=== System Prompt (analyze, zh_TW) ===")
    print(loader.get_system_prompt('analyze', 'zh_TW')[:200] + "...")
    
    print("\n=== User Prompt (analyze, zh_TW) ===")
    user_prompt = loader.get_user_prompt('analyze', 'zh_TW', prompt="測試提示")
    print(user_prompt[:300] + "...")
    
    print("\n=== Dynamic Questions ===")
    test_analysis = {
        "completeness_score": 5,
        "clarity_score": 6,
        "structure_score": 4,
        "specificity_score": 5
    }
    questions = loader.get_dynamic_questions(test_analysis, 'zh_TW')
    for q in questions:
        print(f"[{q['type']}] {q['question']}")
    
    print("\n=== Optimization Strategy ===")
    strategy = loader.get_optimization_strategy('role_enhancement', 'zh_TW', role="專業顧問")
    print(f"Strategy: {strategy}")
    
    print("\nTest completed!")
