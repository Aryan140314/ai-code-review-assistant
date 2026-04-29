import json
import pandas as pd
from pathlib import Path

# Define the root path to the dataset
DATASET_DIR = Path(r"E:\ai-code-review\ml\CodeXGLUE-main\CodeXGLUE-main\Code-Code\Defect-detection\dataset")

def extract_features(code: str):
    """
    Mock feature extraction function. 
    Replace this with your actual logic (e.g., AST parsing, tokenization, line count).
    """
    # Example: returning the number of lines as a feature
    return len(code.strip().split('\n'))

def load_json_data(file_path: Path):
    """Helper to load either a JSON array or JSONL file safely."""
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            # Try parsing as a single JSON Array
            return json.load(f)
        except json.JSONDecodeError:
            # Fallback to parsing as JSON Lines (JSONL)
            f.seek(0)
            return [json.loads(line.strip()) for line in f if line.strip()]

def build_dataset():
    train_jsonl_path = DATASET_DIR / "train.jsonl"
    train_txt_path = DATASET_DIR / "train.txt"
    function_json_path = DATASET_DIR / "function.json"
    
    extracted_data = []

    # ---------------------------------------------------------
    # METHOD 1: Process from train.jsonl (if already pre-processed)
    # ---------------------------------------------------------
    if train_jsonl_path.exists():
        print(f"[*] Found pre-processed data: {train_jsonl_path.name}")
        raw_data = load_json_data(train_jsonl_path)
        
        for idx, item in enumerate(raw_data):
            code = item.get("func", "")
            label = item.get("target", 0)
            features = extract_features(code)
            
            extracted_data.append({
                "code_snippet": code,
                "features": features,
                "label": label
            })
            
            # Debug Print for the first 2 items
            if idx < 2:
                print(f"\n--- Debug: Method 1 (Item {idx}) ---")
                print(f"Label: {label}")
                print(f"Code (First 50 chars): {code[:50].replace(chr(10), ' ')}...")
                
    # ---------------------------------------------------------
    # METHOD 2: Map train.txt IDs to function.json (Raw Format)
    # ---------------------------------------------------------
    elif train_txt_path.exists() and function_json_path.exists():
        print(f"[*] Found raw dataset format. Mapping IDs from {train_txt_path.name} to {function_json_path.name}...")
        
        # Load the master functions list
        all_functions = load_json_data(function_json_path)
        
        # Load the training IDs
        with open(train_txt_path, 'r', encoding='utf-8') as f:
            train_ids = [int(line.strip()) for line in f if line.strip().isdigit()]
            
        print(f"[*] Loaded {len(all_functions)} total functions and {len(train_ids)} train IDs.")
        
        for idx, func_id in enumerate(train_ids):
            try:
                item = all_functions[func_id]
                code = item.get("func", "")
                label = item.get("target", 0)
                features = extract_features(code)
                
                extracted_data.append({
                    "id": func_id,
                    "code_snippet": code,
                    "features": features,
                    "label": label
                })
                
                # Debug Print for the first 2 items
                if idx < 2:
                    print(f"\n--- Debug: Method 2 (Mapped ID {func_id}) ---")
                    print(f"Label: {label}")
                    print(f"Code (First 50 chars): {code[:50].replace(chr(10), ' ')}...")
                    
            except IndexError:
                print(f"[!] Warning: ID {func_id} found in train.txt but is out of bounds for function.json")
    else:
        print("[!] Error: Could not find dataset files.")
        print(f"Please ensure {DATASET_DIR} contains either 'train.jsonl' OR ('function.json' and 'train.txt').")
        return

    # ---------------------------------------------------------
    # Save the Final Dataset
    # ---------------------------------------------------------
    if extracted_data:
        df = pd.DataFrame(extracted_data)
        output_csv = DATASET_DIR / "dataset.csv"
        df.to_csv(output_csv, index=False)
        print(f"\n[+] Success! Extracted {len(df)} samples.")
        print(f"[+] Dataset saved to: {output_csv}")
    else:
        print("\n[-] No data was extracted.")

if __name__ == "__main__":
    build_dataset()