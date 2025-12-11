# Monitoring API

RESTful API для мониторинга серверов написанный на Python.

### Структура проекта

```
monitoring-api/
│
├── src/
│   ├── main.py
│   ├── config.py
│   ├── security/
│   │   ├── admin_jwt.py
│   │   └── agent_key.py
│   ├── api/
│   │   ├── agent.py
│   │   ├── admin.py
│   │   └── router.py
│   ├── models/          # Pydantic-схемы
│   │   ├── agent_models.py
│   │   └── admin_models.py
│   ├── mocks/
│   │   ├── agent_data.py
│   │   └── admin_data.py
│   └── utils/
│       └── responses.py
│
├── .env
├── requirements.txt
└── run.py
```