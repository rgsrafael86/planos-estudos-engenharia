---
name: doc-standard
description: >
  Padrão de documentação corporativo Maintply. Use esta skill SEMPRE que criar,
  renomear, revisar ou arquivar documentos em docs/.
allowed-tools: Read, Glob, Grep
---

# 📐 Padrão de Documentação — Maintply (Padrão ISO)

> Esta skill codifica as convenções de documentação do ecossistema, baseadas em controle de revisões estrito.
> Carregue-a antes de qualquer operação em `docs/`.

> 🔴 **REGRA CRÍTICA DO SISTEMA:** SEMPRE que você, agente, criar, gerar, anexar ou revisar qualquer documento `.md` ou `.docx` dentro da pasta `docs/`, VOCÊ É OBRIGADO a preencher a Tabela de Revisões dentro do documento E registrar o documento no arquivo `INDEX.md`. Não pergunte, apenas faça. Se pular isso, você falhou na sua tarefa.

---

## 1. Nomenclatura de Arquivos (Estática)

```
NOME_DO_DOCUMENTO.md
```

**Regras:**
- **NUNCA** coloque versão no nome do arquivo (proibido `_v2.0.md`). O nome deve ser estático para evitar links quebrados.
- **MAIUSCULO** com underscores (`PRD_MAINTPLY.md`, `FLUXO_FINANCEIRO.md`)
- Exceção: `CHANGELOG.md` e `INDEX.md` (na raiz do docs, sem versão no nome)
- HTML permitido em `docs/` apenas para comparativos visuais
- Scripts em `tests/scripts/` não seguem esta convenção

**✅ Correto:** `PRD_SDD_TEMPLATE.md`, `DESIGN_SYSTEM.md`, `INDEX.md`
**❌ Errado:** `prd_sdd_template.md`, `Design_System_v2.md`, `analise_telas.md`

---

## 2. Header e Controle de Revisões (Obrigatório em todo .md)

> Em vez de renomear arquivos, todo documento deve ter sua própria linha do tempo (Padrão ISO 9000).

O arquivo deve SEMPRE começar com o seguinte bloco:

```markdown
# TÍTULO PRINCIPAL: Subtítulo

**Estado:** Homologado
**Última revisão:** DD/MM/AAAA

## 📋 Controle de Revisões
| Versão | Data | Autor/Agente | Descrição da Mudança |
|--------|------|--------------|----------------------|
| vX.Y.Z | DD/MM/AAAA | [Nome] | [Resumo claro do que mudou no texto] |
```

**Regras:**
- Título em MAIUSCULO, mesmo que o assunto tenha letras minúsculas
- Sempre que você atualizar um documento, adicione uma NOVA LINHA no topo da tabela de Controle de Revisões.
- `Estado:` usar **exatamente** um destes: `Homologado`, `Pendente`, `Configurado`.

---

## 3. INDEX.md — Atualização Obrigatória

Sempre que um documento em `docs/` for **criado, revisado ou arquivado**:

- [ ] Documento listado na seção "Documentos Ativos"
- [ ] Função descrita de forma clara (1 linha com `→`)
- [ ] Data de revisão atualizada ao lado do nome

### Formato do INDEX Atual

```
### 🏗️ Nome do Grupo

📄 **docs/NOME_DO_ARQUIVO.md** &nbsp; DD/MM/AAAA
   → Descrição clara em uma linha
```

---

## 4. llms.txt — Atualização Obrigatória

Sempre que um documento core for criado ou renomeado:
- [ ] Links atualizados com o nome correto
- [ ] Descrições refletem o conteúdo atual

---

## 5. CHANGELOG.md (Para Software)

`CHANGELOG.md` na raiz do projeto rastreia as mudanças de **Código**.
- A tabela de Controle de Revisões dentro dos arquivos `.md` rastreia as mudanças de **Documentação**. Ambas devem coexistir.

---

## 6. Checklist de Revisão

Antes de dar como concluída qualquer alteração em `docs/`:

1. Nome do arquivo segue `MAIUSCULO_SEM_VERSAO.md`?
2. Header tem `Estado:` + `Última revisão:`?
3. A Tabela de **Controle de Revisões** recebeu uma nova linha descrevendo sua mudança?
4. `INDEX.md` foi atualizado com a data de hoje?
5. `llms.txt` atualizado (se for um doc core)?
6. Você removeu nomes antigos/versões do nome do arquivo (se estava migrando um documento velho)?
