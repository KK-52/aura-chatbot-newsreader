import zipfile
import os

def create_zip(zip_name, source_dir):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Exclude directories
            dirs[:] = [d for d in dirs if d not in ['.venv', '__pycache__', '.git', 'chroma_db', '.gemini']]
            
            for file in files:
                if file in ['aura-rag.zip', 'deployment_package.zip', 'create_deploy_package.py', '.env']:
                    continue
                if file.endswith('.zip'):
                    continue
                    
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
                print(f"Added {arcname}")

if __name__ == "__main__":
    create_zip('main.zip', '.')
    print("Created main.zip")
