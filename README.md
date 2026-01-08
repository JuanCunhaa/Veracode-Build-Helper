# Veracode Build Helper

Action facilitadora para padronizar **build + empacotamento em `.zip`** (ex.: `app.zip`) com foco em upload/scan no Veracode.

Criada e mantida por Juan Cunha: https://github.com/JuanCunhaa

## Como usar

Consulte a documentação e exemplos por linguagem/stack em `examples/`.

## Docs por stack (examples)

- .NET: `examples/dotnet/dotnet.md`

## Exemplos

- .NET (publish + package): `examples/dotnet/publish-and-package.yml`
- .NET (multi-projeto via .sln): `examples/dotnet/publish-multi-sln.yml`
- .NET (NuGet feed privado): `examples/dotnet/nuget-private-feed.yml`
- .NET (GitHub Packages): `examples/dotnet/nuget-github-packages.yml`

## Saída padrão

O `.zip` gerado sai sempre em `veracode/` (ex.: `veracode/app.zip`) e é publicado como artifact `veracode-package` (retention = padrão do GitHub).
