#!/usr/bin/env python3
"""
Vetta Dataset Analysis and Summary
Provides comprehensive statistics and insights about the expanded Vetta training dataset.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

def load_dataset(filepath):
    """Load the Vetta dataset from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_dataset(dataset):
    """Perform comprehensive analysis of the dataset."""
    
    print("=== VETTA DATASET ANALYSIS ===\n")
    
    # Basic statistics
    total_examples = len(dataset)
    print(f"Total Examples: {total_examples}")
    
    # Category analysis
    categories = [item.get('category', 'uncategorized') for item in dataset]
    category_counts = Counter(categories)
    
    print(f"\nCategories ({len(category_counts)} total):")
    for category, count in sorted(category_counts.items()):
        percentage = (count / total_examples) * 100
        print(f"  {category}: {count} examples ({percentage:.1f}%)")
    
    # Difficulty analysis
    difficulties = [item.get('difficulty', 'unspecified') for item in dataset]
    difficulty_counts = Counter(difficulties)
    
    print(f"\nDifficulty Levels ({len(difficulty_counts)} total):")
    for difficulty, count in sorted(difficulty_counts.items()):
        percentage = (count / total_examples) * 100
        print(f"  {difficulty}: {count} examples ({percentage:.1f}%)")
    
    # Domain analysis
    domains = [item.get('domain', 'unspecified') for item in dataset]
    domain_counts = Counter(domains)
    
    print(f"\nDomains ({len(domain_counts)} total):")
    for domain, count in sorted(domain_counts.items()):
        percentage = (count / total_examples) * 100
        print(f"  {domain}: {count} examples ({percentage:.1f}%)")
    
    # Instruction/Response length analysis
    instruction_lengths = [len(item['instruction'].split()) for item in dataset]
    response_lengths = [len(item['response'].split()) for item in dataset]
    
    print("\nText Length Statistics:")
    print(f"  Instructions - Avg: {sum(instruction_lengths)/len(instruction_lengths):.1f} words")
    print(f"  Instructions - Min: {min(instruction_lengths)} words")
    print(f"  Instructions - Max: {max(instruction_lengths)} words")
    print(f"  Responses - Avg: {sum(response_lengths)/len(response_lengths):.1f} words")
    print(f"  Responses - Min: {min(response_lengths)} words")
    print(f"  Responses - Max: {max(response_lengths)} words")
    
    # Category by difficulty breakdown
    print("\nCategory by Difficulty Breakdown:")
    category_difficulty = defaultdict(Counter)
    for item in dataset:
        cat = item.get('category', 'uncategorized')
        diff = item.get('difficulty', 'unspecified')
        category_difficulty[cat][diff] += 1
    
    for category in sorted(category_difficulty.keys()):
        print(f"  {category}:")
        for difficulty, count in sorted(category_difficulty[category].items()):
            print(f"    {difficulty}: {count}")
    
    return {
        'total_examples': total_examples,
        'categories': dict(category_counts),
        'difficulties': dict(difficulty_counts),
        'domains': dict(domain_counts),
        'avg_instruction_length': sum(instruction_lengths)/len(instruction_lengths),
        'avg_response_length': sum(response_lengths)/len(response_lengths)
    }

def compare_datasets(original_path, expanded_path):
    """Compare original and expanded datasets."""
    
    print("\n=== DATASET COMPARISON ===\n")
    
    try:
        original = load_dataset(original_path)
        expanded = load_dataset(expanded_path)
        
        print(f"Original Dataset: {len(original)} examples")
        print(f"Expanded Dataset: {len(expanded)} examples")
        print(f"Growth: +{len(expanded) - len(original)} examples ({((len(expanded) - len(original))/len(original)*100):.1f}%)")
        
        # Compare categories
        orig_cats = Counter([item.get('category', 'uncategorized') for item in original])
        exp_cats = Counter([item.get('category', 'uncategorized') for item in expanded])
        
        print("\nCategory Changes:")
        all_categories = set(orig_cats.keys()) | set(exp_cats.keys())
        for cat in sorted(all_categories):
            orig_count = orig_cats.get(cat, 0)
            exp_count = exp_cats.get(cat, 0)
            change = exp_count - orig_count
            if change > 0:
                print(f"  {cat}: {orig_count} → {exp_count} (+{change})")
            elif change < 0:
                print(f"  {cat}: {orig_count} → {exp_count} ({change})")
            else:
                print(f"  {cat}: {exp_count} (unchanged)")
        
    except FileNotFoundError as e:
        print(f"Could not compare datasets: {e}")

def main():
    """Main analysis function."""
    
    # File paths
    expanded_dataset = "data/vetta_comprehensive.json"
    original_dataset = "data/vetta_full.json"
    
    # Analyze expanded dataset
    try:
        dataset = load_dataset(expanded_dataset)
        stats = analyze_dataset(dataset)
        
        # Compare with original
        compare_datasets(original_dataset, expanded_dataset)
        
        print("\n=== VETTA MULTI-PERSONA SYSTEM SUMMARY ===")
        print("\n🎯 MISSION: Transform Vetta from interview-focused AI to comprehensive TalentAI platform orchestrator")
        print("\n📊 DATASET: 453 examples across 15 categories covering full hiring workflow")
        print("\n🤖 PERSONAS: 7 distinct behavioral modes for different platform tasks")
        print("\n🧠 MODEL: IBM Granite 3.0-2B Instruct fine-tuned with LoRA adapters")
        print("\n⚡ TRAINING: Optimized for 1 epoch, 20-30 min training time")
        print("\n🔧 CAPABILITIES:")
        print("  • Sourcing orchestration and agent coordination")
        print("  • Multi-stage candidate interviews")
        print("  • Platform navigation and user guidance")
        print("  • Analytics insights and reporting")
        print("  • Workflow management and process optimization")
        print("  • Deep candidate profiling and assessment")
        print("  • Cross-agent communication and task delegation")
        
        print("\n📁 FILES CREATED:")
        print("  • vetta_comprehensive.json - Expanded training dataset")
        print("  • vetta_persona_prompts.json - 7 persona system prompts")
        print("  • vetta_usage_example.py - Multi-persona usage demonstration")
        print("  • VETTA_IMPLEMENTATION_GUIDE.md - Complete setup and usage guide")
        print("  • granite_fine_tuning_v2.ipynb - Optimized training notebook")
        
        print("\n🚀 NEXT STEPS:")
        print("  1. Execute model training in Colab with expanded dataset")
        print("  2. Test persona switching capabilities")
        print("  3. Deploy to TalentAI platform for integration testing")
        print("  4. Validate performance across all 7 personas")
        print("  5. Monitor and iterate based on real-world usage")
        
    except FileNotFoundError:
        print(f"Dataset file not found: {expanded_dataset}")
        print("Please ensure the dataset has been created.")

if __name__ == "__main__":
    main()
