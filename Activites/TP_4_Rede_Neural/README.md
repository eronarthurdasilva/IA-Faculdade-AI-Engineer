# TP 4 - Rede Neural para Predisposição à Hipertensão

## Execução

No PowerShell, usando Python 3.11:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run_experiment.py
```

O script lê `doc/Hipertensão26.xlsx` e cria a pasta `resultados/` com:

- `relatorio.docx`: documento com metodologia, topologia, resultados, pesos e predições;
- `predicoes.csv`: classe e confiança para cada registro de teste;
- `metricas.json`: métricas completas e configuração da execução;
- `weights.txt`: todos os pesos `Wij` e bias `bi` da rede;
- `modelo.keras`, `historico.png` e `matriz_confusao.png`.

Para repetir com outra quantidade de épocas:

```powershell
python run_experiment.py --epochs 120 --batch-size 32
```