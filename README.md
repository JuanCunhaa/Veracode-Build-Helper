# Veracode Build Helper

Action para padronizar **build + empacotamento em `.zip`** (ex.: `app.zip`) com foco em upload/scan no Veracode.

A estrutura do repo segue o padrão “em camadas”:

- `action.yml`: orquestrador (API de inputs/outputs + ordem do fluxo)
- `internal/`: módulos pequenos e reutilizáveis (cada pasta autocontida)
- `examples/`: catálogo de cenários prontos
- `.github/workflows/release.yml`: automação de release por tag

## Fluxo

1) Roda o módulo da `language` (por enquanto: `dotnet`)
2) Empacota em `output_zip` a partir de `package_paths` (com `exclude_paths`)

Observacoes:

- Esta Action pode instalar o .NET SDK via `actions/setup-dotnet` quando voce informa `dotnet_version`/`dotnet_version_file`. Para outras stacks, use `actions/setup-*` no seu workflow.
- No `dotnet`, a action pode chamar `actions/setup-dotnet` automaticamente se voce informar `dotnet_version` ou `dotnet_version_file`.
- `package_paths`/`exclude_paths` sao globs relativos a `working_directory` e viram paths relativos dentro do zip.

## Linguagens

- .NET -> [abrir](examples/dotnet/dotnet.md)

## Inputs

Todos os booleanos devem ser passados como string: `'true'` / `'false'`.

| Input | Obrigatorio | Default | Notas |
|---|---:|---:|---|
| `language` | nao | `dotnet` | Linguagem/módulo (por enquanto: `dotnet`). |
| `working_directory` | nao | `.` | Base para build e empacotamento. |
| `package_paths` | nao | `''` | Se vazio, usa o default do módulo (no `dotnet`: `${dotnet_publish_dir}/**`). |
| `exclude_paths` | nao | ver `action.yml` | Multiline (globs). |
| `output_zip` | nao | `app.zip` | Relativo ao workspace. |
| `fail_on_empty_zip` | nao | `'true'` | Falha se zip ficar vazio. |

Os inputs específicos de .NET ficam documentados em `examples/dotnet/dotnet.md`.

## Outputs

| Output | Descricao |
|---|---|
| `zip_path` | Caminho do zip gerado (relativo ao workspace). |
| `zip_bytes` | Tamanho do zip em bytes. |
| `zip_files` | Quantidade de arquivos dentro do zip. |
| `build_ran` | `'true'/'false'` indicando se build rodou. |
| `language_effective` | Preset efetivo usado (ou vazio). |
| `dotnet_publish_dir` | Diretório efetivo do publish (relativo ao `working_directory`). |

## Exemplos

- .NET (publish + package) -> [abrir](examples/dotnet/publish-and-package.yml)
