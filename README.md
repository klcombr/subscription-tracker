# SubTrack - Controle suas Assinaturas

**O problema que resolve:** Quantas vezes você já pagou algo e pensou "deixa eu cancelar isso"? Ou simplesmente esqueceu que uma assinatura estava ativa? Com a quantidade de serviços digitais que temos hoje (streaming, musculação, apps, nuvem, coworking), é fácil perder o controle.

**SubTrack** te ajuda a visualizar exatamente quanto você gasta por mês em assinaturas, quais vencem bientôt, e onde está seu maior gasto — tudo numa interface simples e bonita.

## Como funciona

```
Gasto Mensal: R$ 247,90
├── Streaming:      R$ 89,70  (Netflix + Disney+)
├── Produtividade:  R$ 79,90  (Notion + Figma)  
├── Saúde:          R$ 49,90  (Academia)
└── Outros:         R$ 28,40  (Spotify, iCloud...)
```

É rápido de entender e mais rápido ainda de usar.

## Funcionalidades

- **Dashboard com visão geral**: Gasto mensal, anual e próximas renovações
- **Adicionar assinaturas**: Nome, preço, frequência (mensal/anual), categoria e data de vencimento
- **Categorias personalizáveis**: Organize por tipo (Entretenimento, Trabalho, Saúde, etc.)
- **Ativar/Desativar**: Se cancelar uma assinatura, não precisa deletar — só desativa
- **Alerta de vencimento**: Veja o que está pra vencer nos próximos 30 dias
- **Top categoria**: Identifica onde você mais gasta

## Tecnologias

| Camada | Tecnologia |
|--------|------------|
| Backend | Python/FastAPI, SQLite |
| Frontend | Next.js 14, React, TypeScript |

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

API disponível em http://localhost:8000 (docs em /docs)

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App disponível em http://localhost:3000

## Primeiro uso

1. Inicie o backend
2. Inicie o frontend  
3. Na tela inicial, clique em "+ Nova" para adicionar sua primeira assinatura
4. Pronto! Você agora sabe quanto gasta por mês.

## Por que esse projeto?

Todo mundo tem assinaturas. Netflix, Spotify, YouTube Premium, academia, iFood, cloud... Algumas pessoas têm mais de 15. O problema não é gastar — é não saber **onde** e **quanto** do dinheiro está indo todo mês.

Com SubTrack, você consegue:
- Identificar assinaturas esquecidas
- Planejar o orçamento mensal
- Decidir conscientemente quais manter/cancelar
- Ter uma visão clara dos seus gastos recorrentes

Feito com ❤️ para quem quer controle financeiro sem complicação.
