# Personalização do README de perfil

Este arquivo não precisa ser publicado no repositório do perfil. Ele serve só como guia para você.

## OBRIGATÓRIO EDITAR

Tudo isto está no `README.md` e aparece como `[PREENCHER: ...]`. Enquanto algum marcador existir, o perfil não está pronto para publicar.

| Onde | Marcador | O que colocar |
|---|---|---|
| Projetos, bloco 1 | `[PREENCHER: nome do repositório 1]` | Nome real do repositório |
| Projetos, bloco 1 | `[PREENCHER: descrição real do projeto, em uma frase]` | O que o projeto faz, sem exagero |
| Projetos, bloco 1 | `[PREENCHER: tecnologias realmente usadas]` | Só o que o projeto usa de fato |
| Projetos, bloco 1 | `[PREENCHER: URL do repositório 1]` | URL completa, começando com `https://github.com/` |
| Projetos, bloco 2 | os mesmos quatro campos, com "2" | Idem. Se tiver só um projeto, apague o bloco inteiro (as linhas que começam com `>`) |
| Contato | `[PREENCHER: URL do seu perfil no GitHub]` | `https://github.com/` seguido do seu usuário real |
| Contato | `[PREENCHER: URL do seu perfil no LinkedIn]` | URL do perfil, ou apague a linha se não usar |
| Contato | `[PREENCHER: seu e-mail de contato]` | E-mail que você aceita divulgar publicamente, ou apague a linha |

Total: 11 campos a preencher (8 em Projetos, 4 por projeto, e 3 em Contato).

Também é obrigatório, fora dos arquivos: o repositório precisa ter exatamente o mesmo nome do seu usuário do GitHub (ver "Publicar", no fim).

Depois de editar, procure por `PREENCHER` no arquivo. Se não houver nenhum resultado, está completo. Apague também o comentário HTML da seção Projetos (`<!-- ... -->`).

## OPCIONAL EDITAR

- **Texto da seção Sobre.** Mantenha apenas o que for verdadeiro para você.
- **Stack.** O bloco de código é texto simples. Para mudar, edite as linhas. Mantenha Java (ou qualquer item em estudo) em `aprendendo/`. Não crie níveis de domínio que você não possa defender numa entrevista.
- **Cores.** Estão no topo de `tools/gerar_assets.py` (`BG`, `PANEL`, `WHITE`, `GRAY`, `ACID`, `LINE`). Depois de mudar, rode o script de novo (ver abaixo).
- **Frase abaixo do nome no banner.** Procure `desenvolvedor full stack em formação` em `tools/gerar_assets.py`. Se mudar, atualize também o `alt` da imagem no `README.md`.
- **Estatísticas do GitHub.** Não incluí nenhuma de propósito: serviços públicos de estatísticas podem sair do ar ou limitar acessos, e perfis recentes tendem a mostrar números pequenos. Se quiser, adicione depois, seguindo a documentação oficial do serviço escolhido, e sempre com um texto alternativo. Nunca coloque tokens no README.
- **Seções.** Pode remover Projetos ou Contato, mas não deixe títulos vazios.

## NÃO EDITAR SEM NECESSIDADE

- **Estrutura interna dos SVGs** (`assets/*.svg`). Eles são gerados por `tools/gerar_assets.py`. Edição manual é sobrescrita na próxima geração.
- **Caminhos das imagens** no `README.md` (`assets/banner.svg`, `assets/divider.svg`, `assets/signature.svg`). Se mover ou renomear arquivos, atualize aqui também.
- **IDs técnicos** dentro dos SVGs (`kvbanner-t`, `nm1`, `chr1` etc.). Eles ligam título, gradientes e formas.
- **Alfabeto `GLYPHS`** do script. Só tem as letras usadas em KAUAN VENANCIO e KV//OS. Se quiser escrever outras palavras no banner, será preciso desenhar as letras que faltam. O script avisa quais glifos não existem.

## Regenerar os assets

```bash
python tools/gerar_assets.py
```

- Funciona de qualquer diretório. A saída padrão é a pasta `assets/` ao lado de `tools/`.
- **Sobrescreve** `banner.svg`, `divider.svg` e `signature.svg`. Use `--no-overwrite` para abortar se já existirem, ou `--out PASTA` para gravar em outro lugar.
- Requer só Python 3.9 ou superior. Sem instalar pacotes.
- Ao final, o script valida cada SVG (XML, `viewBox`, ausência de scripts e URLs externas, referências internas).

## Publicar no GitHub

O README de perfil só aparece no seu perfil se estiver em um **repositório público com o mesmo nome do seu usuário** (por exemplo, usuário `fulano` → repositório `fulano`).

1. No GitHub, crie um repositório público com o nome exato do seu usuário. Não precisa adicionar README nem licença.
2. Preencha todos os marcadores `[PREENCHER]` (ver acima).
3. Na pasta `github-profile/`, publique somente o necessário:

```bash
git init
git add README.md assets/ tools/
git commit -m "perfil: README KV//OS"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/SEU-USUARIO.git
git push -u origin main
```

   Troque `SEU-USUARIO` pelo seu usuário real nas duas posições. A pasta `assets/` precisa ir junto, porque o README as referencia por caminho relativo.
4. Abra `https://github.com/SEU-USUARIO` e confira o perfil. Confira também no celular e nos temas claro e escuro (Configurações → Aparência).
5. Se o README não aparecer, verifique: o nome do repositório é idêntico ao usuário? O repositório é público? O arquivo se chama `README.md` na raiz?
