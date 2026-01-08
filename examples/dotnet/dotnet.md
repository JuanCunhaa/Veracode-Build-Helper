# .NET (dotnet)

Este modulo faz **restore/build/test/publish** e entrega um diretorio de publish pronto para ser empacotado em `.zip` para o Veracode.

## Como usar (basico)

Use o `dotnet publish` e empacote o output:

- `language: dotnet`
- `dotnet_version` (ou `dotnet_version_file`)
- `dotnet_project` (opcional)
- `dotnet_publish: 'true'` (default)

## Inputs (action principal)

### Seleção do modulo

- `language`: por enquanto use `dotnet`
- `working_directory`: base (default `.`)

### Setup do SDK

- `dotnet_version`: ex.: `8.0.x` (se vazio, nao roda `actions/setup-dotnet`)
- `dotnet_version_file`: ex.: `global.json` (alternativa a `dotnet_version`)

### Alvo

- `dotnet_project`: caminho do `.sln` ou `.csproj` (se vazio, usa `.`)

### Etapas

- `dotnet_restore`: `'true'/'false'` (default `'true'`)
- `dotnet_build`: `'true'/'false'` (default `'false'`)
- `dotnet_test`: `'true'/'false'` (default `'false'`)
- `dotnet_publish`: `'true'/'false'` (default `'true'`)

### Parâmetros comuns

- `dotnet_configuration`: `Release`/`Debug` (default `Release`)
- `dotnet_framework`: ex.: `net8.0`
- `dotnet_runtime`: RID (ex.: `win-x64`, `linux-x64`, `osx-x64`)
- `dotnet_self_contained`: `'true'/'false'` (default `'false'`)

### Publish flags

- `dotnet_publish_single_file`: `'true'/'false'` (default `'false'`)
- `dotnet_publish_trimmed`: `'true'/'false'` (default `'false'`)
- `dotnet_publish_ready_to_run`: `'true'/'false'` (default `'false'`)

### Overrides (avançado)

Se precisar de algo que nao existe como input, use os `*_args` para passar flags extras direto no CLI:

- `dotnet_restore_args`
- `dotnet_build_args`
- `dotnet_test_args`
- `dotnet_publish_args`

### Empacotamento

- `dotnet_publish_dir`: default `publish` (saida do publish, relativo ao `working_directory`)
- `package_paths`: se vazio, usa `${dotnet_publish_dir}/**`
- `output_zip`: default `app.zip`
- `exclude_paths`: lista de globs para ignorar

## Outputs úteis

- `zip_path`, `zip_bytes`, `zip_files`
- `dotnet_publish_dir`

