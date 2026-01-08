# Changelog
 
Todas as mudancas notaveis deste projeto serao documentadas neste arquivo.

O formato e baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adota [Versionamento Semantico](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

## [Unreleased]

### Added

- NuGet: `nuget_sources_json` (mais seguro que `nuget_sources`) e `nuget_auth_mode` (inclui `setup-dotnet` sem `--store-password-in-clear-text`).
- Multi-projeto: filtros `dotnet_projects_include`/`dotnet_projects_exclude`.
- Validações melhores para `publish_multi` e NuGet.
- Saída fixa do zip em `veracode/` e upload como artifact `veracode-package` (retention = padrão do GitHub).

### Changed

- Remove comentários dos arquivos de action e scripts (mantém apenas logs e mensagens de erro).

## [1.0.1] - 2026-01-08

### Changed

- README simplificado para servir como guia breve, com links para docs detalhados em `examples/`.
- Changelog organizado por releases.

## [1.0.0] - 2026-01-08

### Added

- Action orquestradora + empacotamento `.zip` para Veracode.
- Módulo `.NET` (restore/build/test/publish) com setup opcional do SDK.
- MSBuild first-class: `verbosity`, `targets` e `properties`.
- Args robustos (`dotnet_*_args`) com suporte a aspas.
- NuGet/private feeds avançado: `nuget.config` por path/inline e múltiplos sources, além de flags de restore.
- Publish multi-projeto via `.sln` (publica cada projeto em subpastas).
- Branding do Marketplace (`shield`, `purple`).
