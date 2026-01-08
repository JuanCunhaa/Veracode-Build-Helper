# .NET (dotnet)

Este modulo faz **restore/build/test/publish** e entrega um diretorio de publish pronto para ser empacotado em `.zip` para o Veracode.

## Como usar (basico)

Use o `dotnet publish` e empacote o output:

- `language: dotnet`
- `dotnet_version` (ou `dotnet_version_file`)
- `dotnet_project` (opcional)
- `dotnet_publish: 'true'` (default)

## Inputs (action principal)

## Windows vs Ubuntu

O build via `dotnet` funciona em Linux/macOS/Windows (o `dotnet` usa MSBuild internamente).

Quando vale escolher **Windows** no workflow:

- Projetos **.NET Framework** legados (dependem do MSBuild/VS Build Tools);
- Builds que exigem componentes exclusivos do Windows (ex.: alguns targets antigos).

Para projetos modernos (.NET 6/7/8), **Ubuntu** geralmente e suficiente e mais rapido.

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

Os `*_args` suportam aspas e espaços. Para evitar problemas com paths (ex.: `C:\Program Files\...`) prefira usar **multiline** (1 argumento por linha).

### MSBuild (first-class)

- `dotnet_verbosity`: ex.: `minimal`, `normal`, `detailed`, `diagnostic`
- `dotnet_nologo`: `'true'/'false'`
- `dotnet_disable_parallel`: `'true'/'false'`
- `dotnet_msbuild_targets`: ex.: `Build;Publish`
- `dotnet_msbuild_properties`: multiline (ex.: `ContinuousIntegrationBuild=true`)

### Multi-projeto (publish)

Quando `dotnet_publish_multi: 'true'`:

- Se `dotnet_projects` estiver preenchido (multiline), publica cada `.csproj` em `dotnet_publish_dir/<ProjectName>/`.
- Se `dotnet_projects` estiver vazio e `dotnet_project` for `.sln`, usa `dotnet sln <sln> list` para descobrir os projetos e publica todos.
- Você pode filtrar com `dotnet_projects_include` e `dotnet_projects_exclude` (multiline, wildcards).

### NuGet (opcional / private feeds)

Se voce precisa de feed privado, pode:

1) informar um `nuget.config` do repo, ou
2) adicionar um source via inputs.

Inputs:

- `enable_nuget`: `'true'/'false'` ou vazio (vazio = auto quando algum `nuget_*` for informado)
- `nuget_auth_mode`: `dotnet` \| `setup-dotnet` \| `config`
- `nuget_config_path`: path do `nuget.config` (relativo ao `working_directory`)
- `nuget_config_content`: conteudo inline do `nuget.config` (gera arquivo temporario)
- `nuget_source_url`: URL do feed
- `nuget_source_name`: default `private`
- `nuget_username`: default `token`
- `nuget_password`: token/senha (use `secrets.*`)
- `nuget_sources`: multiline `name|url|username|password` (username/password opcionais)
- `nuget_sources_json`: JSON (recomendado; nao quebra com `|` no segredo)
- `nuget_locked_mode`: `'true'/'false'` (restore)
- `nuget_ignore_failed_sources`: `'true'/'false'` (restore)
- `nuget_interactive`: `'true'/'false'` (restore)
- `nuget_packages_dir`: path (restore)
- `nuget_no_cache`: `'true'/'false'` (restore)

Notas:

- `nuget_auth_mode=dotnet`: usa `dotnet nuget add/update source` (para username/password, o `dotnet` exige `--store-password-in-clear-text`, e isso fica apenas no runner do job).
- `nuget_auth_mode=setup-dotnet`: usa `actions/setup-dotnet` + `NUGET_AUTH_TOKEN` (bom para GitHub Packages e feeds por token).
- `nuget_auth_mode=config`: exige `nuget_config_path`/`nuget_config_content` e nao adiciona sources via CLI.

## Feeds comuns

- GitHub Packages: `nuget_auth_mode=setup-dotnet`, `nuget_source_url=https://nuget.pkg.github.com/<OWNER>/index.json`, `nuget_password=${{ secrets.GITHUB_TOKEN }}`.
- Azure Artifacts/Artifactory/Nexus: em geral use `nuget_config_path` ou `nuget_config_content` (modo `config`) e/ou `nuget_sources_json` (modo `dotnet`).

### Empacotamento

- `dotnet_publish_dir`: default `publish` (saida do publish, relativo ao `working_directory`)
- `package_paths`: se vazio, usa `${dotnet_publish_dir}/**`
- `output_zip`: default `app.zip`
- `exclude_paths`: lista de globs para ignorar

## Outputs úteis

- `zip_path`, `zip_bytes`, `zip_files`
- `dotnet_publish_dir`
