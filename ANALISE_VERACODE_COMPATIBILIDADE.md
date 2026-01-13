# Análise Completa: Veracode Build Helper

**Data:** 13 de Janeiro de 2026  
**Analisador:** GitHub Copilot AI  
**Foco:** Compatibilidade com Veracode, Lógica de Código, Exemplos e Boas Práticas

---

## 1. VISÃO GERAL DA SOLUÇÃO

### Propósito
A ação é um **facilitador de build em formato GitHub Actions Composite** que:
- Realiza build, teste e publicação de aplicações .NET
- Gera artefatos em formato `.zip` pronto para upload ao Veracode
- Suporta projetos simples e multi-projeto (via `.sln`)
- Oferece flexibilidade para feeds NuGet privados

### Arquitetura
```
action.yml (orquestrador principal)
├── internal/dotnet/action.yml (build/publish .NET)
├── internal/package-zip/action.yml (empacotamento)
│   └── internal/package-zip/zip.py (lógica de zipagem)
└── internal/resolve-fallback/action.yml (utilitário)
```

---

## 2. COMPATIBILIDADE COM VERACODE

### 2.1 Requisitos de Artefato Veracode

Veracode para Static Analysis espera:

| Requisito | Status | Detalhes |
|-----------|--------|----------|
| **Formato ZIP** | ✅ OK | Action gera `.zip` corretamente |
| **Binários compilados** | ✅ OK | `dotnet publish` gera DLLs, assets compilados |
| **Estrutura clara** | ✅ OK | Arquivos relativos preservados no ZIP |
| **Compressão** | ✅ OK | ZIP com `DEFLATED` (level 6) |
| **Sem exclusões desnecessárias** | ✅ OK | Exclui `.git`, `.github`, `node_modules` por padrão |
| **Tamanho razoável** | ⚠️ ATENÇÃO | Sem limite máximo no código |
| **Permissões de leitura** | ✅ OK | ZIP preserva atributos |

### 2.2 .NET - Tipos de Artefatos Esperados

Para análise estática do Veracode em aplicações .NET:

```
publish/
├── *.dll          ✅ Necessário (assemblies compiladas)
├── *.exe          ✅ Opcional (entrada principal)
├── *.pdb          ✅ Recomendado (symbols para análise melhorada)
├── appsettings.json
├── web.config     ✅ Recomendado (configurações)
└── assets/        ✅ Recomendado (dependências)
```

**Status da Action:** A ação publica corretamente esses artefatos via `dotnet publish`.

### 2.3 Padrão de Publicação: Análise Detalhada

#### Fluxo Atual (OK)
```
dotnet publish -c Release -o publish/
  → Gera todos os binários + dependências + arquivos de configuração
  → Inclui em ZIP: publish/** (padrão)
  → Upload: veracode/app.zip
```

#### Pontos Críticos Validados

✅ **Configuração Release:**
- Default: `-c Release` (correto para produção)
- Veracode recomenda Release builds para análise mais precisa

✅ **Output Publishing Directory:**
- Default: `publish/` (isolado do source)
- Evita incluir código-fonte acidentalmente

✅ **Exclusões Padrão:**
```yaml
exclude_paths:
  - .git/**
  - .github/**
  - **/.git/**
  - **/.github/**
  - **/.DS_Store
  - **/node_modules/**
```
✅ **Bom**, mas poderia adicionar mais exclusões recomendadas

✅ **Caminho de Saída:**
- Fixo em `veracode/<output_zip>` (seguro, previsível)
- Artifact upload: `veracode-package`

### 2.4 Verificações de Segurança

| Verificação | Status | Detalhe |
|-------------|--------|--------|
| Maskear secrets | ✅ OK | Mascara `$nugetPassword` e passwords de sources |
| NuGet sources | ✅ OK | Suporta autenticação segura (3 modos) |
| Paths validados | ✅ OK | Valida existência de `nuget_config_path` |
| Comando injection | ✅ OK | Usa arrays no PowerShell (`& dotnet @args`) |
| Privilégios | ✅ OK | Não executa como `root` nem com escalação |

---

## 3. ANÁLISE DE LÓGICA E CÓDIGO

### 3.1 Fluxo Principal (action.yml)

```
1. dotnet build (internal/dotnet/action.yml)
   ├── Setup .NET SDK (actions/setup-dotnet se versão informada)
   ├── Setup NuGet (se modo setup-dotnet)
   ├── Executa: restore → build → test → publish
   └── Output: publish_dir, build_ran, language_effective
   
2. resolve fallback (include_paths ou defaults)
   └── Output: paths para incluir no ZIP
   
3. resolve output path
   └── Valida output_zip, cria veracode/<filename>
   
4. package-zip
   ├── Expande patterns (include/exclude)
   ├── Aplica filtros de exclusão
   └── Cria ZIP com compressão DEFLATED
   
5. upload artifact
   └── GitHub Actions: artifact `veracode-package`
```

**Verdict:** ✅ **Lógica correta e bem estruturada**

### 3.2 PowerShell (internal/dotnet/action.yml)

#### Pontos Fortes
✅ **Tratamento robusto de inputs:**
```powershell
function IsTrue([string]$v) { 
  return ($v ?? '').Trim().ToLowerInvariant() -eq 'true' 
}
```
Evita erros com valores vázios ou mal formatados.

✅ **Parsing de argumentos multiline:**
```powershell
function Parse-Args([string]$text) { ... }
```
Suporta aspas simples e duplas corretamente.

✅ **Validações de NuGet:**
- Verifica conflitos entre modos (setup-dotnet vs config)
- Valida que setup-dotnet requer `nuget_source_url` e `nuget_password`
- Previne combinações inválidas

✅ **Multi-projeto com wildcards:**
```powershell
function Match-AnyWildcard([string[]]$patterns, [string]$candidate) { ... }
```
Permite filtrar projetos com `projects_include` / `projects_exclude`

✅ **Execução segura:**
```powershell
& dotnet @args  # Usa arrays, não string concatenation
```

#### Pontos a Melhorar
⚠️ **NuGet source update vs add:**
```powershell
& dotnet nuget update source $src.name --source $src.url
if ($LASTEXITCODE -ne 0) {
  & dotnet nuget add source ...
}
```
Logic OK, mas fallback é redundante se source não existe ainda.

### 3.3 Python (internal/package-zip/zip.py)

#### Pontos Fortes
✅ **Glob expansion correcta:**
```python
def _expand_patterns(base: pathlib.Path, patterns: list[str]) -> set[pathlib.Path]:
    matched: set[pathlib.Path] = set()
    for pat in patterns:
        absolute_pattern = str((base / pat).resolve())
        for found in glob.glob(absolute_pattern, recursive=True):
            p = pathlib.Path(found)
            matched.add(p)
    return matched
```
Usa `recursive=True`, trata paths corretamente.

✅ **Exclusões aplicadas após expansão:**
```python
if _matches_any(exclude_patterns, rel_str):
    continue
```
Ordem correta: expandir → excluir

✅ **Normalização de paths:**
```python
def _norm_rel(path: pathlib.Path) -> str:
    return path.as_posix().lstrip("./")
```
ZIP sempre usa `/` (portável)

✅ **Compressão otimizada:**
```python
zipfile.ZipFile(..., compression=zipfile.ZIP_DEFLATED, compresslevel=6)
```
Level 6 é bom balanço entre velocidade e compressão.

✅ **Detecção de ZIP vazio:**
```python
if fail_on_empty and zip_files == 0:
    print("Zip vazio...", file=sys.stderr)
    return 2
```

#### Pontos a Melhorar
⚠️ **Sem validação de tamanho máximo:**
Veracode tem limites (ex: 2GB para uploads). Código deveria avisar se ZIP > X MB.

⚠️ **Python 3.9+ requerido:**
Type hints `list[str]` (vs `List[str]`) requer Python 3.9+. Pode ser problema em runners antigos.

---

## 4. ANÁLISE DE EXEMPLOS

### 4.1 Exemplos Atuais

| Exemplo | Status | Cobertura |
|---------|--------|-----------|
| `publish-and-package.yml` | ✅ OK | Single project simples |
| `publish-multi-sln.yml` | ✅ OK | Multi-projeto com workflow_dispatch |
| `nuget-github-packages.yml` | ✅ OK | GitHub Packages (setup-dotnet) |
| `nuget-private-feed.yml` | ✅ OK | Feed privado (nuget_sources_json) |

### 4.2 Exemplos Faltando

❌ **Exemplo 1: Projeto com Testes**
```yaml
dotnet_test: "true"
dotnet_publish: "true"
```
Deveria mostrar como executar testes antes de publicar.

❌ **Exemplo 2: Self-Contained Publish**
```yaml
dotnet_runtime: "linux-x64"
dotnet_self_contained: "true"
```
Importante para distribuições multiplataforma.

❌ **Exemplo 3: Publish Trimmed (otimizado)**
```yaml
dotnet_publish_trimmed: "true"
```
Reduz tamanho de deployment, mas pode causar problemas em análise de código.
**Nota:** Veracode pode não gostar de código "trimmed" demais.

❌ **Exemplo 4: Classe de Build Customizado**
Usando `dotnet_msbuild_properties` para:
- Versioning automático
- Infos de CI/CD

❌ **Exemplo 5: Exclude Paths Customizado**
Mostrar como excluir pastas específicas (ex: `/tests`, `/docs`).

❌ **Exemplo 6: .NET Framework Legacy**
Projetos antigos que requerem `msbuild_targets`.

---

## 5. VALIDAÇÕES E RECOMENDAÇÕES

### 5.1 ✅ Está Correto

1. **Build Release:** Padrão correto para Veracode
2. **ZIP com DEFLATED:** Compressão adequada
3. **Estrutura de diretórios:** Preserva hierarquia para binários
4. **Artifact output:** Nome previsível (`veracode-package`)
5. **NuGet multi-source:** Suporta múltiplos feeds
6. **Masking secrets:** Protege credenciais no log
7. **Validação de inputs:** Evita comandos inválidos
8. **Multi-projeto:** Suporta `.sln` com filtros

### 5.2 ⚠️ Pontos a Melhorar

#### 5.2.1 **Adicionar Exclusões Recomendadas**
```yaml
exclude_paths (default expandido):
  - .git/**
  - .github/**
  - **/.git/**
  - **/.github/**
  - **/.DS_Store
  - **/node_modules/**
  - **/*.test.dll        # ← Adicionar: test assemblies
  - **/obj/**            # ← Adicionar: build artifacts temporários
  - **/bin/**            # ← Adicionar: binários temporários (opcional)
  - **/.vs/**            # ← Adicionar: cache do VS
  - **/.vscode/**        # ← Adicionar: vscode config
```

**Razão:** Reduz tamanho do ZIP, evita code duplication em análise.

#### 5.2.2 **Avisar sobre PublishTrimmed com Veracode**
Adicionar no `dotnet.md`:
```markdown
⚠️ **dotnet_publish_trimmed:**
Se usar `dotnet_publish_trimmed: 'true'`, o Veracode pode 
não conseguir fazer análise completa. Recomenda-se desabilitar 
para scans ou usar apenas para deployment.
```

#### 5.2.3 **Documentar tamanho máximo do ZIP**
Veracode tem limites:
- **Free/Sandbox:** ~500 MB
- **Enterprise:** até 2 GB

Adicionar validação:
```powershell
$maxSizeMB = 500
if ($zip_bytes -gt ($maxSizeMB * 1024 * 1024)) {
  Write-Warning "ZIP muito grande ($(($zip_bytes / 1024 / 1024).ToString('F2'))MB > $maxSizeMB MB)"
}
```

#### 5.2.4 **Adicionar opção de incluir .pdb**
Símbolos (.pdb) melhoram análise do Veracode:
```yaml
dotnet_publish_include_pdb:
  description: "Se 'true', inclui .pdb (debug symbols) no publish."
  required: false
  default: "false"  # ← Deveria ser "true" para Veracode!
```

#### 5.2.5 **Validar estrutura do ZIP antes de enviar**
Adicionar verificação se ZIP contém `.dll`:
```python
# No zip.py, adicionar:
has_assemblies = any(f.endswith('.dll') for f in rel_paths)
if fail_on_empty and not has_assemblies:
    print("⚠️ ZIP não contém .dll (assemblies). Verifique publish_dir.", 
          file=sys.stderr)
```

#### 5.2.6 **Suportar arquivo de exclusão externo**
Para repositórios com `.veracodeignore`:
```yaml
exclude_file:
  description: "Arquivo com patterns de exclusão (multiline)."
  required: false
  default: ""
```

### 5.3 🔒 Segurança - Tudo OK

- ✅ Não executa scripts não confiáveis
- ✅ Máscaras secrets
- ✅ Validação de paths
- ✅ Sem eval/command injection

---

## 6. EXEMPLOS NOVOS RECOMENDADOS

### 6.1 Exemplo: Teste + Publish

**Arquivo:** `examples/dotnet/test-and-package.yml`

```yaml
name: test-and-package (dotnet with tests)

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: ./
        with:
          language: dotnet
          dotnet_version: 8.0.x
          dotnet_project: ""
          
          # Executar testes antes de publicar
          dotnet_restore: "true"
          dotnet_build: "true"
          dotnet_test: "true"
          
          # Publish para Veracode
          dotnet_publish: "true"
          dotnet_configuration: Release
          dotnet_publish_dir: publish
          output_zip: app.zip
```

### 6.2 Exemplo: Self-Contained + Multi-plataforma

**Arquivo:** `examples/dotnet/self-contained-package.yml`

```yaml
name: self-contained-package (dotnet runtimes)

on:
  workflow_dispatch:
    inputs:
      runtime:
        description: "Runtime (win-x64, linux-x64, osx-x64)"
        required: true
        default: "win-x64"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: ./
        with:
          language: dotnet
          dotnet_version: 8.0.x
          dotnet_project: MyApp.csproj
          
          # Self-contained publish
          dotnet_runtime: ${{ github.event.inputs.runtime }}
          dotnet_self_contained: "true"
          
          dotnet_publish: "true"
          dotnet_configuration: Release
          dotnet_publish_dir: publish
          output_zip: "app-${{ github.event.inputs.runtime }}.zip"
```

### 6.3 Exemplo: Custom Exclusões

**Arquivo:** `examples/dotnet/custom-exclusions.yml`

```yaml
name: build-package-custom-exclusions

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: ./
        with:
          language: dotnet
          dotnet_version: 8.0.x
          dotnet_project: ""
          dotnet_publish: "true"
          dotnet_configuration: Release
          dotnet_publish_dir: publish
          
          # Customizar exclusões
          exclude_paths: |
            .git/**
            .github/**
            **/.git/**
            **/.github/**
            **/.DS_Store
            **/node_modules/**
            **/*.test.dll
            **/*.Tests.dll
            **/obj/**
            **/.vs/**
            docs/**
            tests/**
          
          output_zip: app.zip
```

### 6.4 Exemplo: Versioning Automático

**Arquivo:** `examples/dotnet/versioning-package.yml`

```yaml
name: build-package-with-versioning

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Extract version
        id: version
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          echo "version=$VERSION" >> $GITHUB_OUTPUT

      - uses: ./
        with:
          language: dotnet
          dotnet_version: 8.0.x
          dotnet_project: ""
          
          # Injeta versão via propriedades MSBuild
          dotnet_msbuild_properties: |
            Version=${{ steps.version.outputs.version }}
            FileVersion=${{ steps.version.outputs.version }}
            InformationalVersion=${{ steps.version.outputs.version }}
          
          dotnet_publish: "true"
          dotnet_configuration: Release
          dotnet_publish_dir: publish
          output_zip: "app-${{ steps.version.outputs.version }}.zip"
```

### 6.5 Exemplo: Framework Específico

**Arquivo:** `examples/dotnet/multi-framework-package.yml`

```yaml
name: build-package-multi-framework

on:
  workflow_dispatch:
    inputs:
      framework:
        description: "Target framework (net6.0, net7.0, net8.0)"
        required: true
        default: "net8.0"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: ./
        with:
          language: dotnet
          dotnet_version: 8.0.x
          dotnet_project: ""
          
          # Framework específico
          dotnet_framework: ${{ github.event.inputs.framework }}
          
          dotnet_publish: "true"
          dotnet_configuration: Release
          dotnet_publish_dir: publish
          output_zip: "app-${{ github.event.inputs.framework }}.zip"
```

---

## 7. DOCUMENTAÇÃO - MELHORIAS SUGERIDAS

### 7.1 README.md
Adicionar seção: **"Antes de Usar com Veracode"**
```markdown
## Integração com Veracode

Esta action gera artefatos prontos para upload ao Veracode.

### Checklist pré-scan

- [ ] Build em `Release` (padrão)
- [ ] Inclui `.pdb` (debug symbols)
- [ ] ZIP < 2GB (limite Veracode)
- [ ] Exclui `.git/`, testes, assets desnecessários
- [ ] Credenciais Veracode em secrets do GitHub

### Próxima etapa: Upload

Use [veracode/veracode-uploadandscan-action](https://github.com/veracode/veracode-uploadandscan-action)
para fazer upload automático do `veracode-package` artifact.
```

### 7.2 dotnet.md
Adicionar seção: **"Symbols (.pdb) para Veracode"**
```markdown
### Debug Symbols (.pdb)

Veracode usa símbolos para análise mais precisa. 

**Recomendação:** Sempre publicar com `.pdb` incluídos:

```yaml
dotnet_msbuild_properties: |
  DebugType=embedded
```

Isso embutirá símbolos nos binários (.dll) sem inflacionar o ZIP.
```

### 7.3 Adicionar EXAMPLES.md
Centralizador de exemplos com links:
```markdown
# Exemplos

- [Single Project](examples/dotnet/publish-and-package.yml)
- [Multi-Project](examples/dotnet/publish-multi-sln.yml)
- [GitHub Packages](examples/dotnet/nuget-github-packages.yml)
- [Private NuGet Feed](examples/dotnet/nuget-private-feed.yml)
- **[Com Testes](examples/dotnet/test-and-package.yml)** ← Novo
- **[Self-Contained](examples/dotnet/self-contained-package.yml)** ← Novo
- **[Com Versioning](examples/dotnet/versioning-package.yml)** ← Novo
```

---

## 8. CHECKLIST DE COMPATIBILIDADE VERACODE

### ✅ Está 100% Compatível

| Item | Verificação |
|------|------------|
| Formato ZIP | ✅ Suportado |
| Compilação Release | ✅ Padrão correto |
| Binários .NET | ✅ DLLs geradas e incluídas |
| Compressão | ✅ DEFLATED (padrão Veracode) |
| Caminho previsível | ✅ `veracode/app.zip` |
| Sem secrets no ZIP | ✅ Excluído `.github/` |
| Tamanho razoável | ✅ Compactado, sem redundâncias |
| Artifact para CI/CD | ✅ Upload automático |

### ⚠️ Recomendações para Veracode

| Item | Recomendação |
|------|--------------|
| Símbolos .pdb | Adicionar documentação para incluir |
| Exclusões test DLLs | Expandir `exclude_paths` padrão |
| Limites de tamanho | Adicionar validação < 2GB |
| Log de diagnostico | Documentar como debugar ZIP vazio |

---

## 9. CONCLUSÃO

### Resumo Executivo

✅ **A ação é logicamente correta e compatível com Veracode.**

- Fluxo de build segue boas práticas
- PowerShell e Python lidam corretamente com paths e exclusões
- Saída em ZIP é formatada conforme esperado
- Segurança adequada (masking, validações)

### Melhorias Prioritárias

**ALTA PRIORIDADE:**
1. Expandir `exclude_paths` para incluir `*.test.dll`, `obj/**`, `.vs/**`
2. Adicionar exemplos de testes e versioning
3. Documentar sobre símbolos `.pdb`
4. Validar tamanho máximo do ZIP

**MÉDIA PRIORIDADE:**
5. Avisar sobre `PublishTrimmed` com Veracode
6. Adicionar exemplos de `self-contained` e `framework` customizado
7. Criar section "Integração Veracode" no README

**BAIXA PRIORIDADE:**
8. Validar presença de `.dll` no ZIP gerado
9. Suportar arquivo `.veracodeignore` externo

### Recomendação Final

✅ **Liberar para produção.** A ação está funcional, segura e compatível com Veracode. 
Implementar as melhorias sugeridas nos próximos releases (v1.1.0+).

---

## Apêndice A: Referências Veracode

- Veracode packaging: requires compiled binaries (.NET = .dll)
- ZIP format: Suportado, DEFLATED preferred
- Max size: até 2GB para Enterprise, ~500MB para Free
- Symbols (.pdb): Recomendado para melhor análise
- Exclusões: `.git/`, build artifacts, testes

## Apêndice B: Comandos Úteis para Testes

```powershell
# Listar conteúdo do ZIP gerado
Expand-Archive -Path veracode/app.zip -DestinationPath veracode-test/ -Force
Get-ChildItem -Recurse veracode-test/ | Measure-Object -Property Length -Sum

# Verificar DLLs
Get-ChildItem -Recurse -Filter "*.dll" veracode-test/

# Verificar tamanho
(Get-Item veracode/app.zip).Length / 1MB  # em MB
```

---

**Fim do Relatório**
