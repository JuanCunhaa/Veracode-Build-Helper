# Changelog
 
Todas as mudancas notaveis deste projeto serao documentadas neste arquivo.

O formato e baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adota [Versionamento Semantico](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

## [Unreleased]

### Added

- Scaffold inicial da action (modulo `.NET` + empacotamento `.zip`).
- Suporte opcional a NuGet/private feeds (via `nuget.config` ou `dotnet nuget add source`).
- Args robustos (`dotnet_*_args`) com suporte a aspas.
- MSBuild first-class (verbosity, targets e properties).
- Publish multi-projeto (solution -> publica cada projeto em subpastas).
