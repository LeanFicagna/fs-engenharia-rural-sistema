# FS Consultoria Rural: site institucional

Site estático (HTML, CSS e JavaScript puros) da FS Consultoria Rural, consultoria rural no oeste do Pará.
Publicado em <https://www.fsengenhariarural.com.br> (domínio no arquivo `CNAME`).

## Como rodar localmente

Não há build nem dependências. Abra a pasta no VS Code e use a extensão **Live Server** no `index.html`,
ou rode qualquer servidor estático na raiz, por exemplo:

```bash
python -m http.server 5500
```

O Swiper (carrossel) e o Font Awesome (ícones) vêm de CDN, então é preciso internet.

## Estrutura

```
index.html            página única
404.html              página de erro (o GitHub Pages usa automaticamente)
robots.txt, sitemap.xml
CNAME                 domínio personalizado
css/
  reset.css, base.css, variables.css
  components/         um arquivo por seção (navbar, hero, services, contact-form...)
  alternativas/       estilos guardados para uso futuro, fora do index.html (ex.: valores-numerados.css)
script/
  config.js           WhatsApp e URL da planilha: o que costuma mudar
  layout.js           menu e ano do rodapé
  contact.js          formulário de contato e links do WhatsApp
  projects.js         trabalhos por serviço
  video.js            vídeo de apresentação
  services-carousel.js  carrossel de "Nossos serviços"
  service-details.js  janela com os detalhes de cada serviço (abre ao clicar no card)
img/                  logo, hero, servicos, equipe, trabalhos, fundos
apps-script/          script do Google que registra o formulário na planilha e envia email
```

Os arquivos de `script/` são scripts comuns (sem `import`), carregados com `defer` na ordem do `index.html`.
O `config.js` precisa vir primeiro.

## Configurações

| O quê | Onde |
|---|---|
| Número do WhatsApp | `script/config.js` → `whatsappNumber` |
| URL do formulário na planilha | `script/config.js` → `sheetsEndpoint` (passo a passo em `apps-script/README.md`) |
| Cores, fontes, altura da barra | `css/variables.css` |
| Vídeo de apresentação | `index.html`, bloco `video-block`: coloque o arquivo em `video/` e descomente o `<source>` |
| Fotos por serviço | `index.html`, bloco `projects-grid`: cada `<img>` tem `data-service` (`georreferenciamento`, `car`, `credito`), com o arquivo em `img/trabalhos/` (até 1000 px). Para um serviço novo, inclua também o botão em `projects-menu` e o nome em `SERVICE_NAMES` (`script/projects.js`) |
| Fotos da galeria do dia a dia | `index.html`, lista `team-gallery__more`: um `<li>` por foto, com o arquivo em `img/equipe/galeria/` (WebP, até 1400 px), a legenda em `data-caption` e a descrição no texto do link. Elas aparecem só na galeria em tela cheia, depois das 4 fotos da grade |
| Detalhes de cada serviço | `index.html`, dentro de cada card de "Nossos serviços": bloco `service-card__details` (escondido), com o texto, "Para quem é" e "O que inclui". A janela mostra esse bloco ao clicar no card |

Enquanto `sheetsEndpoint` estiver vazio, o formulário só abre o WhatsApp e não registra na planilha.

## Convenções

- **Imagens:** nomes em minúsculas, com hífen e sem acento (`dia-a-dia-1.webp`), dentro da subpasta do uso.
  Use WebP, redimensione para o tamanho em que aparecem (o dobro, para telas de alta densidade) e informe
  `width` e `height` no `<img>`. Abaixo da primeira tela, use `loading="lazy"`.
- **CSS:** um arquivo por seção em `css/components/`, com um `<link>` próprio no `index.html` (a ordem importa;
  não use `@import`, que baixa os arquivos em fila). Cores da marca como variável
  (`--color-logo-green`, `--color-neutral-10`) em vez de valor solto.
- **Variantes de layout:** para testar uma ideia visual, crie uma página separada (por exemplo `xx_nome.html`) e só aplique
  no `index.html` quando aprovada. Não deixe essas páginas no repositório.

## Publicação

O site é servido pelo GitHub Pages a partir da branch **`develop`**: cada `push` nela publica as mudanças.
A `main` serve de ponto de backup (merge da `develop` na `main` quando uma etapa está estável).

## Pendências conhecidas

- Publicar o Apps Script e preencher `sheetsEndpoint`.
- Colocar o vídeo de apresentação (hoje há só a capa com o botão de play).
- Fotos reais para cada serviço em "Veja alguns dos nossos trabalhos" (hoje repetem as mesmas três imagens).
