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
- .NET (com testes): `examples/dotnet/test-and-package.yml` ← Novo
- .NET (self-contained): `examples/dotnet/self-contained-package.yml` ← Novo
- .NET (framework específico): `examples/dotnet/multi-framework-package.yml` ← Novo
- .NET (com versionamento): `examples/dotnet/versioning-package.yml` ← Novo
- .NET (symbols otimizados): `examples/dotnet/symbols-optimized-package.yml` ← Novo
- .NET (custom exclusões): `examples/dotnet/custom-exclusions.yml` ← Novo

## Saída padrão

O `.zip` gerado sai sempre em `veracode/` (ex.: `veracode/app.zip`) e é publicado como artifact `veracode-package` (retention = padrão do GitHub).

## Verificação de Compatibilidade Veracode

✅ Esta action gera artefatos **100% compatíveis** com Veracode para análise estática.

- Binários compilados (.NET = .dll, .exe)
- ZIP com compressão DEFLATED
- Estrutura de diretórios preservada
- Debug symbols opcionais (.pdb)
- Exclusões automáticas (.git, testes, etc)

Para detalhes técnicos, veja [ANALISE_VERACODE_COMPATIBILIDADE.md](ANALISE_VERACODE_COMPATIBILIDADE.md).

## Integração com Veracode (Próximas Etapas)

1. **Gere o ZIP** com esta action → `veracode/app.zip`
2. **Upload para Veracode** com:
   ```yaml
   - uses: veracode/veracode-uploadandscan-action@v2
     with:
       filepath: veracode/app.zip
       vid: ${{ secrets.VERACODE_API_ID }}
       vkey: ${{ secrets.VERACODE_API_KEY }}
   ```
3. **Acompanhe resultados** no dashboard Veracode
