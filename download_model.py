from huggingface_hub import hf_hub_download
import os

def download_model():
    repo_id = "QuantFactory/Meta-Llama-3-8B-Instruct-GGUF"
    filename = "Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"
    
    os.makedirs("models", exist_ok=True)
    
    print(f"Downloading {filename} from {repo_id}...")
    model_path = hf_hub_download(
        repo_id=repo_id, 
        filename=filename, 
        local_dir="models",
        local_dir_use_symlinks=False
    )
    print(f"Model successfully downloaded to: {model_path}")

if __name__ == "__main__":
    download_model()
