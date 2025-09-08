# tools/prompt_loader.py
def cargar_prompt(path="prompts/auria_prompt.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
