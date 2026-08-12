import sys
import json
import re

def validate(html_path):
    print(f"Validando: {html_path}")
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        match = re.search(r'<script id="studyPlanData" type="application/json">\s*({[\s\S]*?})\s*</script>', content)
        if not match:
            print("[ERRO] Bloco JSON 'studyPlanData' nao encontrado no HTML.")
            sys.exit(1)
            
        try:
            plan = json.loads(match.group(1))
        except Exception as e:
            print(f"[ERRO] Falha ao fazer o parse do JSON: {e}")
            sys.exit(1)
            
        errors = []
        
        # 1. Modulos
        modules = plan.get("modules", [])
        if len(modules) < 1:
            errors.append("O plano deve possuir pelo menos 1 modulo.")
            
        # 2. Questoes (Regra estrita de 6)
        questions = plan.get("questions", [])
        if len(questions) < 6:
            errors.append(f"O plano possui apenas {len(questions)} questoes. A regra estrita exige NO MINIMO 6 questoes.")
            
        for idx, q in enumerate(questions):
            opts = q.get("options", [])
            if len(opts) != 4:
                errors.append(f"A questao {idx+1} ({q.get('id')}) possui {len(opts)} alternativas. Deve possuir exatamente 4.")
                
        # 3. Videos
        has_video = False
        for m in modules:
            if len(m.get("videos", [])) > 0:
                has_video = True
                break
        
        if not has_video:
            errors.append("O plano deve conter pelo menos 1 video validado.")
            
        if errors:
            print("[FALHA NA VALIDACAO]")
            for err in errors:
                print(f" - {err}")
            sys.exit(1)
            
        print("[SUCESSO] Plano validado com perfeicao!")
        sys.exit(0)

    except Exception as e:
        print(f"[ERRO FATAL] Erro ao abrir ou ler o arquivo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python validate_plan.py <caminho_para_index.html>")
        sys.exit(1)
    validate(sys.argv[1])
