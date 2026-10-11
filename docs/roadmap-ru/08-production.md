# Продакшен (Production)

## Контейнеризация (Containerization)
Источник: [узел "Containerization" на roadmap.sh](https://roadmap.sh/inference-engineering/containerization@--ohScNmF5LR04P8e95AP)

Контейнеризация упаковывает сервис инференса и все его зависимости в Docker-образ, который одинаково работает в любом окружении. Контейнеры для инференса включают CUDA toolkit, Python-пакеты, движок инференса и системные библиотеки вроде ffmpeg для обработки аудио. Зафиксированное дерево зависимостей защищает работающие сервисы от ломающих изменений и даёт воспроизводимые сборки.

Ресурсы:
- [Docker Documentation](https://docs.docker.com/) (официальная документация)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/) (официальная документация)
- [What is containerization?](https://www.ibm.com/think/topics/containerization) (статья)
- [Containerization Explained](https://www.youtube.com/watch?v=0qotVMX-J5s) (видео)

### Управление зависимостями (Dependency Management)
Источник: [узел "Dependency Management" на roadmap.sh](https://roadmap.sh/inference-engineering/dependency-management@wEaM8VyAo6MFsc3RXQ7Ar)

Цепочки зависимостей инференса длинные и хрупкие из-за тесной связи версий CUDA, версий фреймворков и архитектур железа. Фиксация точных версий всех зависимостей защищает от неожиданных поломок, когда upstream-пакеты выпускают обновления. Контейнеры для только что вышедших моделей часто поначалу зависят от предрелизных сборок, и их приходится пересобирать на стабильных релизах в течение нескольких дней после запуска модели.

Ресурсы:
- [Kubernetes Documentation](https://kubernetes.io/docs/home/) (официальная документация)
- [Dependency Management](https://www.baseten.co/inference-engineering/book/07-production/containerization/#dependency-management) (статья)
- [Production in Inference Engineering](https://inferenceengineering.tech/chapters/production/) (статья)

### NIMs
Источник: [узел "NIMs" на roadmap.sh](https://roadmap.sh/inference-engineering/nims@KB7ExU9X49omOuk9D_Qal)

NIMs это готовые Docker-контейнеры от NVIDIA для популярных открытых моделей; они доступны как гибкие мульти-LLM контейнеры или как оптимизированные контейнеры под конкретные GPU и модели. Они дают готовую стартовую точку для сервинга распространённых архитектур без сборки собственного контейнера с нуля. Для максимального контроля и нестандартных конфигураций обычно лучше начать с более нейтрального базового образа и достраивать его.

Ресурсы:
- [NVIDIA NIM for Developers](https://developer.nvidia.com/nim) (официальная документация)
- [NVIDIA NIM Microservices](https://www.nvidia.com/en-us/ai-data-science/products/nim-microservices/) (официальная документация)
- [NVIDIA NIM in Docker](https://docs.docker.com/ai/docker-agent/providers/nvidia/) (официальная документация)
- [How to Self-Host LLMs and Multi-Modal AI Models with NVIDIA NIM in 5 Minutes](https://www.youtube.com/watch?v=087spL8hMvM&t=59s) (видео)

## Автомасштабирование (Autoscaling)
Источник: [узел "Autoscaling" на roadmap.sh](https://roadmap.sh/inference-engineering/autoscaling@o_gotSHKIPtV5SgGN3Vja)

Автомасштабирование динамически подстраивает число активных реплик модели под входящий трафик: держит SLA по задержке и сводит к минимуму траты на простаивающие GPU. Kubernetes, стандартный слой оркестрации, масштабирует реплики внутри кластера по сигналам трафика и метрикам утилизации. Ключевые параметры конфигурации: минимум реплик, максимум реплик, окно автомасштабирования, задержка перед уменьшением числа реплик и целевая конкурентность на реплику.

Ресурсы:
- [Autoscaling endpoints for LLM inference](https://www.together.ai/blog/autoscaling-endpoints-for-llm-inference) (статья)
- [Autoscaling Inference Endpoints](https://apxml.com/courses/mlops-for-large-models-llmops/chapter-4-llm-deployment-serving-optimization/autoscaling-inference-endpoints) (статья)
- [Best practices for autoscaling large language model (LLM) inference workloads](https://docs.cloud.google.com/kubernetes-engine/docs/best-practices/machine-learning/inference/autoscaling) (статья)
- [Autoscaling your AI agent under load](https://www.youtube.com/watch?v=ESIL0Rzl5VQ&t=91s) (видео)

### Непрерывный батчинг (Continuous Batching)
Источник: [узел "Continuous Batching" на roadmap.sh](https://roadmap.sh/inference-engineering/continuous-batching@h_PDOMA-V-n7Pab3epuP3)

Непрерывный батчинг (continuous batching) работает на уровне токенов: запросы входят в батч и выходят из него по мере завершения отдельных токенов, а не после того, как закончится весь батч. Так GPU остаётся загруженным, а штраф по задержке от батчинга минимален по сравнению со статическим или динамическим батчингом. Все основные движки инференса реализуют непрерывный батчинг по умолчанию.

Ресурсы:
- [Continuous batching](https://huggingface.co/blog/continuous_batching) (статья)
- [Continuous Batching: Optimizing LLM Inference Throughput](https://mbrenndoerfer.com/writing/continuous-batching) (статья)
- [How to Scale LLM Applications With Continuous Batching!](https://www.youtube.com/watch?v=PqHVpvvHLpE) (видео)
- [Continuous Batching - How LLM Servers Keep the GPU Full](https://www.youtube.com/watch?v=X8CwAqYxH1E) (видео)

### Холодные старты (Cold Starts)
Источник: [узел "Cold Starts" на roadmap.sh](https://roadmap.sh/inference-engineering/cold-starts@Q3zM9MN5lmHRAUWjdLdXR)

Холодный старт это время от нуля реплик до обслуживания первого запроса, включая выделение GPU, загрузку образа контейнера, загрузку весов модели и запуск или компиляцию движка инференса. Сокращать время холодного старта необходимо, чтобы система автомасштабирования уверенно уменьшала число реплик и быстро наращивала его. Ключевые техники: квантованные веса, локальный кеш весов рядом с GPU-инстансами и кеширование скомпилированных движков инференса на диск.

Ресурсы:
- [Autoscaling endpoints for LLM inference](https://www.together.ai/blog/autoscaling-endpoints-for-llm-inference) (статья)
- [Autoscaling for LLM Inference Serving and Cold Starts](https://www.onesourcecloud.net/cms/autoscaling-llm-inference-serving-cold-starts.html) (статья)
- [GPU Cold Start on Serverless LLM Inference: 4 Fixes That Actually Work (2026)](https://www.spheron.network/blog/gpu-cold-start-llm-inference-2026/) (статья)

### Маршрутизация и балансировка нагрузки (Routing and Load Balancing)
Источник: [узел "Routing & Load Balancing" на roadmap.sh](https://roadmap.sh/inference-engineering/routing-load-balancing@DSyTAtFC1TvC1P7yD10Nb)

Маршрутизаторы принимают решения на уровне запроса: на какую реплику его отправить с учётом совпадения префикса в KV-кеше и доступности LoRA. Балансировщики нагрузки принимают решения на уровне системы и распределяют трафик по репликам равномерно. В системах с префиксным кешированием наивный round-robin упускает возможности кеша; умная маршрутизация повышает долю попаданий в кеш и снижает TTFT.

Ресурсы:
- [LLM Inference Serving: Architecture, Routing & Auto-Scaling](https://mbrenndoerfer.com/writing/llm-inference-serving-architecture-scaling-optimization) (статья)
- [LLM Model Routing: Route Queries to the Right Model Automatically](https://neuraltrust.ai/blog/llm-model-routing) (статья)
- [LLM Load Balancing: Concepts, Strategies & Best Practices](https://www.truefoundry.com/blog/llm-load-balancing) (статья)
- [Auto Routing Fully Explained](https://www.youtube.com/watch?v=2M47nZbyhac) (видео)

### Маршрутизация с учётом LoRA (LoRA-Aware Routing)
Источник: [узел "LoRA-Aware Routing" на roadmap.sh](https://roadmap.sh/inference-engineering/lora-aware-routing@KdceJEDBdy3TbzG5suE38)

Веса LoRA-дообучения это небольшие адаптерные слои, которые загружаются поверх базовой модели, чтобы специализировать её под конкретную задачу или клиента. Деплой, который обслуживает много LoRA-вариантов одной базовой модели, должен направлять каждый запрос на реплику, где нужный LoRA-адаптер уже загружен в память GPU. Маршрутизация без этого знания заставляет постоянно менять LoRA-адаптеры, что добавляет задержку и снижает пропускную способность каждой затронутой реплики.

Ресурсы:
- [Unsupervised LoRA Routing](https://www.emergentmind.com/topics/unsupervised-lora-routing) (статья)
- [Intelligent LoRA Routing](https://vllm-sr.ai/docs/v0.1/tutorials/intelligent-route/lora-routing/) (статья)
- [What is Low-Rank Adaptation (LoRA)](https://www.youtube.com/watch?v=DhRoTONcyZE) (видео)

### Очередь запросов (Request Queueing)
Источник: [узел "Request Queueing" на roadmap.sh](https://roadmap.sh/inference-engineering/request-queueing@k-zXOGynI0B0yyT-n3raa)

Очередь запросов удерживает входящий трафик, когда все активные реплики загружены до предела, пока автомасштабирование поднимает новые. Стандартная реализация: очередь FIFO (первым пришёл, первым обслужен). Очереди с приоритетами могут давать платным пользователям лучшее место. Очередь должна быть видна только что запущенным репликам, чтобы запросы не ждали существующих реплик, когда новая ёмкость уже доступна.

Ресурсы:
- [Efficient Request Queueing - Optimizing LLM Performance](https://huggingface.co/blog/tngtech/llm-performance-request-queueing) (статья)
- [LLM Request Queuing](https://gigagpu.com/llm-request-queuing-concurrent-users/) (статья)
- [Why Do AI Requests Queue? | Inside vLLM](https://www.youtube.com/watch?v=MmRalL3oHMM) (видео)

### Масштабирование до нуля (Scale to Zero)
Источник: [узел "Scale to Zero" на roadmap.sh](https://roadmap.sh/inference-engineering/scale-to-zero@Pi87dWgu5NTIJRQUc169s)

Масштабирование до нуля (scale to zero) позволяет системе держать ноль реплик в периоды без трафика и поднимать их по требованию. Для этого нужны быстрые холодные старты и надёжная очередь, которая удержит входящие запросы, пока реплика стартует. Масштабирование до нуля хорошо подходит для сред разработки и периодически используемых нагрузок, но не для чувствительных к задержке продакшен-приложений с непредсказуемым лёгким трафиком.

Ресурсы:
- [Should LLM Serving Scale to Zero for Cost](https://www.onesourcecloud.net/cms/should-llm-serving-scale-to-zero-cost.html) (статья)
- [Runpod Secrets: Scaling LLM Inference to Zero Cost During Downtime](https://www.runpod.io/articles/guides/runpod-secrets-scale-llm-inference-zero-cost) (статья)
- [Zero Redundancy Optimizer (ZeRO): Scaling LLM Training Without Breaking the Bank](https://medium.com/@adilmaqsood501/zero-redundancy-optimizer-zero-scaling-llm-training-without-breaking-the-bank-ba045b6a805e) (статья)

### Независимое масштабирование компонентов (Independent Component Scaling)
Источник: [узел "Indep. Component Scaling" на roadmap.sh](https://roadmap.sh/inference-engineering/indep-component-scaling@SKs0yuBEAyeTPQxLll3EM)

В мультимодельных пайплайнах, например в голосовом агенте, который последовательно запускает VAD, ASR, LLM и TTS, компоненты различаются требованиями к железу и паттернами трафика. Каждый компонент должен автомасштабироваться независимо, по собственной нагрузке. Запуск всех компонентов в одном Kubernetes-кластере сводит к минимуму сетевую задержку между ними, а иначе она может съесть заметную часть жёсткого бюджета задержки.

Ресурсы:
- [Autoscaling Workloads](https://kubernetes.io/docs/concepts/workloads/autoscaling/) (официальная документация)
- [Autoscaling endpoints for LLM inference](https://www.together.ai/blog/autoscaling-endpoints-for-llm-inference) (статья)
- [Intro to Kubernetes Autoscaling and Best Practices for Implementations](https://www.cloudbolt.io/kubernetes-autoscaling/) (статья)

## Мультиоблако (Multi-Cloud)
Источник: [узел "Multi-Cloud" на roadmap.sh](https://roadmap.sh/inference-engineering/multi-cloud@d78UiI_FZyLsU6O52btXg)

Мультиоблачный инференс распределяет GPU-ёмкость по провайдерам и регионам, чтобы повысить доступность, снизить задержку и выполнить требования локализации данных (data residency). Группа охватывает стратегию закупок, управление ёмкостью, географическую маршрутизацию и паттерны надёжности, благодаря которым крупномасштабный инференс переживает сбои железа и провайдеров.

Ресурсы:
- [How to Do Agentic AI Inference in a Multicloud, Multi-Model World](https://blog.equinix.com/blog/2025/03/19/how-to-do-agentic-ai-inference-in-a-multicloud-multi-model-world/) (статья)
- [What is multicloud?](https://cloud.google.com/learn/what-is-multicloud?hl=en) (статья)
- [Multi-Cloud GPU Strategy: How to Avoid AI Infrastructure Vendor Lock-In](https://lyceum.technology/magazine/multi-cloud-gpu-avoid-vendor-lock-in/) (статья)
- [What is Multicloud? How Do You Manage It?](https://www.youtube.com/watch?v=AjtdZ3gFRjU) (видео)

### Закупка GPU (GPU Procurement)
Источник: [узел "GPU Procurement" на roadmap.sh](https://roadmap.sh/inference-engineering/gpu-procurement@4mbGBgTu8AtrFHVYiffkB)

Облачные GPU доступны у гиперскейлеров вроде AWS и GCP, у GPU-ориентированных неооблаков вроде CoreWeave и Nebius и на вторичных рынках. Механизмы закупки: зарезервированные инстансы со скидкой для предсказуемой базовой нагрузки, инстансы по требованию для гибкости и спотовые инстансы для чувствительных к стоимости батч-нагрузок, которые переживают вытеснение. Крупные деплои обычно сочетают все три варианта у нескольких провайдеров.

Ресурсы:
- [Multi-Cloud GPU Strategy: How to Avoid AI Infrastructure Vendor Lock-In](https://lyceum.technology/magazine/multi-cloud-gpu-avoid-vendor-lock-in/) (статья)
- [Multi-Cloud GPU Strategy: Definition, Benefits, and Implementation](https://compux.net/docs/concepts/multi-cloud-gpu-strategy/) (статья)

### Управление ёмкостью (Capacity Management)
Источник: [узел "Capacity Management" на roadmap.sh](https://roadmap.sh/inference-engineering/capacity-management@xrr5Y1sbN2eyQyuA5LlAW)

Мультиоблачный инференс объединяет GPU-ёмкость нескольких облачных провайдеров и регионов в один планируемый ресурс и рассматривает разные пулы вычислений как взаимозаменяемые. Для этого нужен глобальный control plane, который принимает решения о деплое и масштабировании, и workload plane в каждом кластере, которые обслуживают трафик и отчитываются об утилизации. Настоящее мультиоблако даёт больше суммарной ёмкости, выше надёжность за счёт избыточности, ниже задержку за счёт географической близости и соответствие требованиям суверенитета данных.

Ресурсы:
- [How we built Multi-cloud Capacity Management (MCM)](https://www.baseten.co/blog/how-we-built-multi-cloud-capacity-management/) (статья)
- [Multi-cloud capacity management](https://learn-inference.com/chapters/production/multi-cloud) (статья)

### Балансировка нагрузки с учётом географии (Geo-Aware Load Balancing)
Источник: [узел "Geo-Aware Load Balancing" на roadmap.sh](https://roadmap.sh/inference-engineering/geo-aware-load-balancing@mzF2mHSj8cvr9mvr16R0N)

Глобальный балансировщик нагрузки направляет запросы в GPU-кластер, географически ближайший к пользователю. Сетевая задержка растёт примерно на 5 миллисекунд за каждый пройденный часовой пояс, поэтому маршрут запроса из Сингапура в Сан-Франциско добавляет от 50 до 100 миллисекунд лишних накладных расходов. Маршрутизация с учётом географии гарантирует, что свободная ёмкость в далёком регионе используется только когда ближняя исчерпана.

Ресурсы:
- [How Geographic Load Balancing Improves Performance](https://www.serverion.com/uncategorized/how-geographic-load-balancing-improves-performance/) (статья)
- [Geo-aware load balancing](https://www.baseten.co/resources/guide/the-baseten-inference-stack/#geo-aware-load-balancing) (статья)

### Безопасность и соответствие требованиям (Security and Compliance)
Источник: [узел "Security and Compliance" на roadmap.sh](https://roadmap.sh/inference-engineering/security-and-compliance@4x-4BFZH7bfNteD5ZAwTI)

Инфраструктура инференса должна защищать пользовательский ввод, выходы модели и её веса. Стандартные практики: шифрование данных, безопасность контейнеров, сетевая изоляция и контроль доступа, проверенные сторонним пентестом. Регулируемым отраслям нужно соответствие фреймворкам вроде SOC 2 и HIPAA, и это распространяется и на облачных провайдеров. Мультиоблачные деплои поддерживают требования локализации данных: данные каждой страны направляются в кластеры внутри этой страны.

Ресурсы:
- [Inference security: How to protect APIs in production AI systems](https://www.gmicloud.ai/zh-tw/blog/inference-security-how-to-protect-apis-in-production-ai-systems) (статья)
- [How to achieve compliance and security in AI inference](https://gcore.com/blog/compliance-and-security-in-ai-inference) (статья)
- [Are your AI Inference and GenAI Environments Secure? These Five Essentials Will Help](https://www.a10networks.com/blog/are-your-ai-inference-and-genai-environments-secure/) (статья)

## Тестирование и деплой (Testing and Deployment)
Источник: [узел "Testing & Deployment" на roadmap.sh](https://roadmap.sh/inference-engineering/testing-deployment@ZlOtQtxJST10nuHjhbUx6)

Чтобы безопасно разворачивать сервисы инференса, нужны инструменты для выкатки изменений без простоя, оценки стоимости до выбора конфигурации и контроля состояния системы после запуска. Группа охватывает вопросы деплоя, стоимости, наблюдаемости (observability) и соответствия требованиям, которые встают, когда сервис готов к продакшен-трафику.

Ресурсы:
- [Testing and Deployment AI Models](https://www.baseten.co/inference-engineering/book/07-production/testing-and-deployment/) (статья)

### Деплой без простоя (Zero-Downtime Deployment)
Источник: [узел "Zero-Downtime Deplo." на roadmap.sh](https://roadmap.sh/inference-engineering/zero-downtime-deplo@le4sPQ0h9l-vlmCB4G8ZY)

Канареечная выкатка (canary) обновляет сервисы инференса без прерывания живого трафика: небольшой процент запросов направляется на новый деплой, его мониторят на проблемы и постепенно переводят трафик целиком. Blue-green деплой, который разом переключает весь трафик на параллельное окружение, непрактичен для крупных инференс-нагрузок, потому что на время перехода нужно удвоить GPU-ёмкость. С автомасштабированием канареечная выкатка обходится дёшево: старый сервис уменьшает число реплик по мере того, как новый принимает трафик.

Ресурсы:
- [Zero-Downtime Deployments: A Practical Guide for Busy Engineers](https://medium.com/codetodeploy/zero-downtime-deployments-a-practical-guide-for-busy-engineers-2d7b43f1a2bc) (статья)
- [How do software systems achieve zero downtime on new deploys?](https://www.youtube.com/watch?v=BiuQ-sVbWGU) (статья)
- [Zero Downtime Deployments in Kubernetes Explained](https://www.youtube.com/watch?v=Tb1x1KtyVww) (статья)

### Оценка стоимости (Cost Estimation)
Источник: [узел "Cost Estimation" на roadmap.sh](https://roadmap.sh/inference-engineering/cost-estimation@Gof4kW2LbkNCtH68c7Xvq)

Стоимость выделенного инференса зависит от размера батчей, паттернов трафика и длин последовательностей, а не от одного лишь числа токенов. Чтобы сравнить выделенный инференс с API, нужно пересчитать потокенную цену API в общую стоимость за репрезентативное окно времени и сопоставить её со стоимостью GPU-часов при том же объёме трафика. Полная стоимость владения включает и время инженеров на создание и поддержку системы инференса.

Ресурсы:
- [The Hidden Economics of LLM Inference](https://www.hebbia.com/blog/the-hidden-economics-of-llm-inference) (статья)
- [LLM Inference Benchmarking: How Much Does Your LLM Inference Cost?](https://developer.nvidia.com/blog/llm-inference-benchmarking-how-much-does-your-llm-inference-cost/) (статья)
- [LLM inference cost: what drives it and how to lower it](https://www.cloudzero.com/blog/inference-cost/) (статья)
- [LLM Cost Calculation Guide for Enterprise AI Teams in 2026](https://www.digitalocean.com/resources/articles/llm-cost-calculation-guide) (статья)

### Наблюдаемость (Observability)
Источник: [узел "Observability" на roadmap.sh](https://roadmap.sh/inference-engineering/observability@w-dVv5dFNxD7Rqy16m4uL)

Наблюдаемость (observability) инференса отслеживает общий объём запросов, длины входных и выходных последовательностей, коды ответов, перцентили задержки (P50, P90, P99 для TTFT, TPS и сквозной задержки), число реплик, утилизацию GPU и глубину очереди. Эти метрики взаимозависимы: всплеск задержки может быть вызван длинными входными последовательностями, высокой конкурентностью или проблемой с железом. Наблюдаемость должна интегрироваться с существующими инструментами вроде Grafana, Datadog и PagerDuty, чтобы метрики инференса были видны в контексте.

Ресурсы:
- [NVIDIA Nsight Systems](https://developer.nvidia.com/nsight-systems) (официальная документация)
- [LLM Observability: A Complete Guide to Monitoring Production Deployments](https://inference.net/content/llm-observability-monitoring-production-deployments/) (статья)
- [What is LLM Observability? The Ultimate Guide for AI Developers](https://www.comet.com/site/blog/llm-observability/) (статья)
- [Understanding LLM Observability](https://clickhouse.com/resources/engineering/llm-observability) (статья)
