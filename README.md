# Base_feedback

Ferramenta em Python para consolidar avaliações 360° orientadas a valores segundo a política da Alvo BR.

## Requisitos

- Python 3.10+

## Instalação

Crie e ative um ambiente virtual (opcional) e instale as dependências do projeto (nenhuma dependência externa é necessária).

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\\Scripts\\activate  # Windows PowerShell
```

## Uso

1. Prepare um arquivo JSON seguindo o schema esperado (ver `examples/sample_input.json`).
2. Execute o script principal informando o caminho do arquivo.

```bash
python main.py examples/sample_input.json
```

Para salvar a saída em um arquivo:

```bash
python main.py examples/sample_input.json --output resultado.json
```

## Estrutura do Projeto

- `alvo_eval/` – pacote com a lógica de cálculo de scores, classificação e geração de alertas.
- `examples/` – exemplos de entrada para facilitar a adoção.
- `main.py` – ponto de entrada via linha de comando.

## Testando rapidamente

```bash
python main.py examples/sample_input.json
```

O comando acima imprime o JSON final com `score_final`, classificações e alertas calculados automaticamente.
