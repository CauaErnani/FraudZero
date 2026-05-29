# FraudZero - API de Detecção de Fraudes PIX e Cartões em Tempo Real

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-179C3A?style=for-the-badge)

**Nota de Ineditismo Acadêmico:** Por questões de propriedade intelectual e regras para submissão em periódico científico, este repositório contém apenas a estrutura arquitetural e as rotas da API. O código completo do modelo XGBoost, os algoritmos de balanceamento e a base de treinamento são mantidos em ambiente privado.

## Sobre o Projeto
O **FraudZero** é uma API Restful projetada para atuar como uma camada intermediária de segurança, capaz de realizar a detecção de fraudes em transações digitais (como PIX e cartões de crédito) em tempo real. A pesquisa busca utilizar algoritmo de classificação supervisionada (XGBoost) para superar as limitações de sistemas tradicionais baseados em regras fixas, otimizando as taxas de detecção de anomalias e mitigando perdas financeiras.

Este sistema foi desenvolvido como projeto de pesquisa (Iniciação Científica e TCC) na área de Sistemas de Informação, sob a orientação do Prof. Dr. Renato Correia de Barros e em coautoria com Pedro Henrique da Silva Batista.

## Arquitetura e Modelagem de Dados
A inteligência e a engenharia de software do sistema foram construídas unindo modelagem estatística a uma arquitetura de alta disponibilidade:
* **Modelo Preditivo:** Treinamento realizado com o classificador **XGBoost**, utilizando a técnica **SMOTE** (Imbalanced-learn) para tratar o desbalanceamento de classes no dataset.
* **Framework Web:** O core da aplicação foi construído em **FastAPI**, garantindo uma arquitetura assíncrona para que a análise de risco ocorra com latência inferior a 200ms.
* **Persistência de Logs:** Utilização de **PostgreSQL** gerenciado via **SQLAlchemy (asyncio)** para registro de logs de auditoria e scores de risco.
* **Segurança e Autenticação:** Implementação de autenticação via **PyJWT** e hash de senhas utilizando **Pwdlib com Argon2**.
* **Infraestrutura:** Orquestração dos serviços e padronização do ambiente isolado utilizando **Docker** e **Docker Compose**.

## Funcionalidades da API (Vitrine)
* Recebimento de payloads de transações financeiras via requisições HTTP POST.
* Pré-processamento e normalização de atributos em tempo real (Mock na versão pública).
* Retorno do *score* de risco e classificação (Legítima ou Fraude) respeitando a janela de tempo dos ecossistemas bancários digitais.
