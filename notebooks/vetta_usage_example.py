#!/usr/bin/env python3
"""
Vetta Multi-Persona Usage Example
Demonstrates how to use the fine-tuned Vetta model with different personas
for various TalentAI platform tasks.
"""

import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from unsloth import FastLanguageModel
import os

class VettaOrchestrator:
    """Multi-persona Vetta AI orchestrator for TalentAI platform."""
    
    def __init__(self, model_path="./vetta_granite_fine_tuned"):
        """Initialize Vetta with the fine-tuned model."""
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.persona_prompts = self._load_persona_prompts()
        
    def _load_persona_prompts(self):
        """Load persona system prompts from JSON file."""
        try:
            with open("data/vetta_persona_prompts.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: Persona prompts file not found. Using default prompts.")
            return {}
    
    def load_model(self):
        """Load the fine-tuned Vetta model."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}")
            
        print("Loading Vetta model...")
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.model_path,
            max_seq_length=2048,
            dtype=None,
            load_in_4bit=True,
        )
        FastLanguageModel.for_inference(self.model)
        print("Model loaded successfully!")
    
    def switch_persona(self, persona_name):
        """Switch to a specific persona."""
        if persona_name not in self.persona_prompts:
            available_personas = list(self.persona_prompts.keys())
            raise ValueError(f"Persona '{persona_name}' not found. Available: {available_personas}")
        
        self.current_persona = persona_name
        self.system_prompt = self.persona_prompts[persona_name]
        print(f"Switched to {persona_name} persona")
        return self.system_prompt
    
    def generate_response(self, user_input, max_new_tokens=512, temperature=0.7):
        """Generate a response using the current persona."""
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        if not hasattr(self, 'current_persona'):
            raise RuntimeError("No persona selected. Call switch_persona() first.")
        
        # Format the prompt with system message and user input
        prompt = f"<|system|>\n{self.system_prompt}\n<|user|>\n{user_input}\n<|assistant|>\n"
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode response
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the assistant's response (after the last <|assistant|>)
        response_start = full_response.rfind("<|assistant|>")
        if response_start != -1:
            response = full_response[response_start + len("<|assistant|>"):]
        else:
            response = full_response
        
        return response.strip()

def main():
    """Demonstrate Vetta multi-persona capabilities."""
    
    # Initialize Vetta
    vetta = VettaOrchestrator()
    
    try:
        # Load the model (uncomment when model is trained)
        # vetta.load_model()
        
        # Example 1: Sourcing Orchestrator
        print("\n=== Sourcing Orchestrator Example ===")
        vetta.switch_persona("sourcing_orchestrator")
        user_query = "I need to find 5 senior Python developers for our fintech startup. Can you coordinate the sourcing agents?"
        print(f"User: {user_query}")
        # response = vetta.generate_response(user_query)
        print("Vetta: [Response would be generated here with model loaded]")
        
        # Example 2: Candidate Interviewer
        print("\n=== Candidate Interviewer Example ===")
        vetta.switch_persona("candidate_interviewer")
        interview_question = "Can you walk me through your experience with microservices architecture?"
        print(f"Interviewer: {interview_question}")
        # response = vetta.generate_response(interview_question)
        print("Vetta: [Response would be generated here with model loaded]")
        
        # Example 3: Platform Navigator
        print("\n=== Platform Navigator Example ===")
        vetta.switch_persona("platform_navigator")
        navigation_query = "How do I schedule an interview and view the candidate's analytics?"
        print(f"User: {navigation_query}")
        # response = vetta.generate_response(navigation_query)
        print("Vetta: [Response would be generated here with model loaded]")
        
        # Example 4: Analytics Insights
        print("\n=== Analytics Insights Example ===")
        vetta.switch_persona("analytics_insights")
        analytics_query = "What are our key hiring metrics for the last quarter?"
        print(f"User: {analytics_query}")
        # response = vetta.generate_response(analytics_query)
        print("Vetta: [Response would be generated here with model loaded]")
        
        print("\n=== Multi-Persona Demo Complete ===")
        print("To run with actual model, ensure the fine-tuned model is available at ./vetta_granite_fine_tuned")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the model is trained and available, or run this as a demonstration.")

if __name__ == "__main__":
    main()
