# Painel Nutrify Connect · Acompanhamento de Alunos

Painel interativo e analítico para acompanhamento do progresso, engajamento e retenção dos colaboradores matriculados no programa **Nutrify Connect** (contas `@nutrify.com.br` e `@integralmedica.com`).

---

## 🚀 Como Funciona a Publicação e Automação

* **Hospedagem**: O painel é publicado diretamente via **GitHub Pages**.
* **Automação (GitHub Actions)**: O fluxo `.github/workflows/atualizar_dashboard.yml` roda automaticamente de segunda a sexta (ou sob demanda clicando em *Run workflow*), consulta a API da Academy, filtra a base e atualiza a página online sem necessidade de intervenção manual.
* **Acesso**: Disponível em computadores e dispositivos móveis com suporte a filtros, busca e exportação CSV.

---

## 🛠️ Execução Local

Caso deseje atualizar os dados e executar o painel na sua própria máquina:

1. Atualizar dados da API:
```bash
python atualizar_dashboard_nutrify.py
```

2. Abrir o arquivo `index.html` em qualquer navegador.
