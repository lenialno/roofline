# Базовая терминология (Basic Terminology)

## Метрики задержки (Latency Metrics)

### Время до первого токена (Time to First Token, TTFT)
Источник: [узел "Time to First Token" на roadmap.sh](https://roadmap.sh/inference-engineering/time-to-first-token@xCgNhwbS_ELxEyRHD1enO)

TTFT измеряет, сколько времени проходит от отправки запроса до получения пользователем первого выходного токена. Его определяют в первую очередь фаза prefill и время в очереди. Для стриминговых приложений вроде чат-ботов TTFT: самый заметный сигнал задержки, он напрямую влияет на ощущение отзывчивости.

Ресурсы:
- [What is time to first token (TTFT)?](https://www.ibm.com/think/topics/time-to-first-token) (статья)
- [What Is Time to First Token?](https://www.cerebras.ai/glossary/what-is-time-to-first-token) (статья)
- [Most devs don't understand how LLM tokens work](https://www.youtube.com/watch?v=nKSk_TiR8YA) (видео)

### Токены в секунду (Tokens Per Second, TPS)
Источник: [узел "Tokens Per Second" на roadmap.sh](https://roadmap.sh/inference-engineering/tokens-per-second@uxm_BIAyhfFmcE94k9i9J)

TPS измеряет, сколько токенов в секунду получает пользователь после первого токена. Его определяет фаза decode, и он отражает эффективность использования пропускной способности памяти. TPS на пользователя (его ещё называют воспринимаемым TPS) это метрика задержки; суммарный TPS по всему сервису инференса: метрика пропускной способности.

Ресурсы:
- [What Are Tokens per Second?](https://www.cerebras.ai/glossary/what-are-tokens-per-second) (статья)
- [Tokens Per Second](https://www.taskade.com/wiki/ai/tokens-per-second) (статья)
- [LLM Speed Tiers Explained: What TPS (Token Per Second) Actually Feels Like](https://www.youtube.com/watch?v=EZE-2xYpvOw) (видео)

### Межтокенная задержка (Inter-Token Latency, ITL)
Источник: [узел "Inter-Token Latency" на roadmap.sh](https://roadmap.sh/inference-engineering/inter-token-latency@sre_s0dvpOP0DTM66a3hu)

ITL это время между соседними сгенерированными токенами в фазе decode. ITL в 10 миллисекунд соответствует 100 токенам в секунду. Это пошаговая мера, лежащая в основе TPS; она напрямую зависит от того, как быстро GPU выполняет один прямой проход decode.

Ресурсы:
- [Inter-Token Latency - NVIDIA](https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html#inter-token-latency) (статья)
- [Inter-Token Latency](https://nhimg.org/glossary/inter-token-latency/) (статья)

### Задержка и пропускная способность (Latency vs. Throughput)
Источник: [узел "Latency vs. Throughput" на roadmap.sh](https://roadmap.sh/inference-engineering/latency-vs-throughput@kvNIi3aY5rn69_hYkDyUK)

Меньшая задержка означает более быстрые ответы для каждого пользователя; большая пропускная способность: больше запросов, обслуженных за единицу времени. Эти цели часто конфликтуют. Увеличение размера батча повышает пропускную способность, но ухудшает задержку для каждого пользователя. Выбор правильного баланса: одно из главных решений при настройке сервиса инференса.

Ресурсы:
- [The LLM Inference Trilemma: Throughput, Latency, Cost](https://www.digitalocean.com/blog/llm-inference-tradeoffs) (статья)
- [LLM inference latency: TTFT, tokens per second, and what to measure](https://clickhouse.com/resources/engineering/llm-inference-latency) (статья)
- [Latency vs Throughput: Deep Dive into System Performance Trade‑Offs](https://medium.com/@shivanimutke2501/%EF%B8%8F-latency-vs-throughput-deep-dive-into-system-performance-trade-offs-adcd5860dc56) (статья)
- [Latency vs Throughput in 60 Seconds](https://www.youtube.com/watch?v=azUdQ9bme9g) (видео)

### Перцентили задержки (Latency Percentiles)
Источник: [узел "Latency Percentiles" на roadmap.sh](https://roadmap.sh/inference-engineering/latency-percentiles@8y280d5BPXrDZwtsHZCaX)

Средняя задержка скрывает выбросы. Время ответа LLM распределено с правым хвостом, поэтому инженеры измеряют P50, P90, P95 и P99. P99 в несколько секунд означает, что каждый сотый пользователь получает плохой опыт, даже если медиана быстрая. Снижать задержку P90/P99 так же важно, как и среднюю.

Ресурсы:
- [Percentiles vs averages: why your latency dashboard lies](https://clickhouse.com/resources/engineering/percentiles-vs-averages) (статья)
- [Latency percentiles for load testing analysis](https://gatling.io/blog/latency-percentiles-for-load-testing-analysis) (статья)
- [Mastering Latency Metrics: P90, P95, P99 | System Design](https://www.youtube.com/watch?v=lJ4NEMNBeS4) (видео)

### Сквозные метрики (End-to-End Metrics)
Источник: [узел "End-to-End Metrics" на roadmap.sh](https://roadmap.sh/inference-engineering/end-to-end-metrics@tENGACXKSKVPmZy9a3D2z)

Сквозная задержка включает время инференса, сетевой round-trip, время в очереди и накладные расходы на стороне клиента. Метрики только инференса показывают, насколько хорошо работает сервер модели; сквозные метрики показывают, что реально видит пользователь. Если инференс быстрый, а сквозное время большое, узкое место в инфраструктуре или клиентском коде, а не в GPU.

Ресурсы:
- [10 LLM Inference Metrics Every AI Engineer Must Know](https://www.intoai.pub/p/llm-inference-metrics) (статья)

### Коэффициент реального времени (Real-Time Factor, RTF)
Источник: [узел "Real-Time Factor" на roadmap.sh](https://roadmap.sh/inference-engineering/real-time-factor@0-BRllrMiShLlytidGkST)

RTF измеряет, насколько быстро система ASR обрабатывает аудио относительно его длительности. Система, которая транскрибирует час аудио за шесть секунд, имеет RTF 600x. Это стандартная метрика пропускной способности для транскрипции длинных файлов; она растёт примерно линейно с числом GPU, которые параллельно обрабатывают фрагменты.

Ресурсы:
- [What is RTF (Real-Time Factor) in ASR?    Copied from: https://www.futurebeeai.com/knowledge-hub/real-time-factor-asr](https://www.futurebeeai.com/knowledge-hub/real-time-factor-asr) (статья)
- [Whisper Real-Time Factor by GPU](https://gigagpu.com/whisper-rtf-by-gpu/) (статья)
- [RTF - Real-Time Factor Explained](https://transcript.you/glossary/rtf) (статья)

## Фазы инференса (Inference Phases)

### Фазы prefill и decode (Prefill and Decode Phases)
Источник: [узел "Prefill & Decode Phases" на roadmap.sh](https://roadmap.sh/inference-engineering/prefill-decode-phases@hwKZmfYFiIu6plbiXtJRI)

У инференса LLM две разные фазы. Prefill обрабатывает всю входную последовательность параллельно, строит KV-кеш и ограничен вычислениями. Decode генерирует выходные токены по одному, читая веса модели из памяти, и ограничен пропускной способностью памяти. У каждой фазы свои узкие места, и на каждую действуют свои техники оптимизации.

Ресурсы:
- [Prefill vs Decode: LLM Inference Phases Explained](https://redis.io/blog/prefill-vs-decode/) (статья)
- [Understanding the Two Key Stages of LLM Inference: Prefill and Decode(Part-1)](https://medium.com/@sailakkshmiallada/understanding-the-two-key-stages-of-llm-inference-prefill-and-decode-29ec2b468114) (статья)
- [Why LLMs Read Fast but Write Slowly - Prefill vs Decode](https://www.youtube.com/watch?v=hmMgTgQpO38) (видео)

### Онлайн- и офлайн-инференс (Online vs. Offline Inference)
Источник: [узел "Online vs. Offline Inf." на roadmap.sh](https://roadmap.sh/inference-engineering/online-vs-offline-inf@SkvPauxjmqok4TyNWSACL)

Онлайн-инференс обслуживает пользовательские запросы в реальном времени, где важна задержка. Офлайн-инференс асинхронно обрабатывает большие батчи данных, где пропускная способность и стоимость важнее скорости отдельного запроса. Одной и той же модели, например Whisper для транскрипции, могут понадобиться отдельные развёртывания под каждый сценарий, потому что оптимальные конфигурации сильно различаются.

Ресурсы:
- [Production ML systems: Static versus dynamic inference](https://developers.google.com/machine-learning/crash-course/production-ml-systems/static-vs-dynamic-inference) (статья)
- [Trade-offs in Online vs Offline Model Inference](https://bugfree.ai/knowledge-hub/trade-offs-online-vs-offline-model-inference) (статья)
- [Offline Recurrence for Improved Online Inference](https://www.youtube.com/watch?v=bwvE1KvLzLQ) (видео)

### Асинхронный инференс (Asynchronous Inference)
Источник: [узел "Asynchronous Inference" на roadmap.sh](https://roadmap.sh/inference-engineering/asynchronous-inference@59mMKSva9vkoMxHErNXOd)

Асинхронный инференс это модель запросов fire-and-forget: клиент отправляет задание, сразу получает подтверждение, а результат забирает позже через вебхук. Она подходит для нагрузок, где важна пропускная способность, а не задержка: массовое построение эмбеддингов документов или транскрипция корпуса. У асинхронных заданий намного более длинные лимиты по времени, чем у синхронных запросов, и им нужна надёжная очередь на стороне сервера.

Ресурсы:
- [Using asynchronous inference in production](https://www.baseten.co/blog/using-asynchronous-inference-in-production/) (статья)
- [Asynchronous Inference: Methods & Applications](https://www.emergentmind.com/topics/asynchronous-inference) (статья)

## Контекст приложения (Application Context)

### AI-native приложения (AI-Native Applications)
Источник: [узел "AI-Native Applications" на roadmap.sh](https://roadmap.sh/inference-engineering/ai-native-applications@ZqFQmNizkU6ykTMCrmTWf)

AI-native приложения это продукты, где генеративные модели лежат в основе пользовательского опыта: редакторы кода, голосовые агенты, поддержка клиентов, генерация медиа. У каждой категории свои требования к инференсу. Агенты делают много вызовов инференса на одно действие пользователя; чат-приложения ставят в приоритет TTFT; голосовым приложениям нужна низкая сквозная задержка для естественного разговора.

Ресурсы:
- [Visit the Dedicated AI Product Builder Roadmap](https://roadmap.sh/ai-product-builder) (roadmap)
- [What is AI native?](https://www.ibm.com/think/topics/ai-native) (статья)
- [Guide to Building AI-Native Applications](https://talkdev.com/learning-center/guide-to-building-ai-native-applications) (статья)
- [How to Build an AI-Native Services Company](https://www.youtube.com/watch?v=gSNFJbgoaHI) (видео)

### Потребительские и B2B-нагрузки (Consumer vs. B2B Workloads)
Источник: [узел "Consumer vs. B2B" на roadmap.sh](https://roadmap.sh/inference-engineering/consumer-vs-b2b@SFMvVdgTZv_POWFGWWM_s)

Потребительские приложения чувствительны к стоимости и переживают непредсказуемые всплески трафика, поэтому им нужны гибкое автомасштабирование и низкая предельная стоимость. B2B-приложения ставят в приоритет аптайм и стабильно низкую задержку, потому что часто стоят на критическом пути процессов, приносящих выручку. Требования комплаенса, включая локализацию данных и регуляторные сертификации, чаще встречаются в корпоративных развёртываниях.

Ресурсы:
- [Consumer vs. B2B](https://www.baseten.co/inference-engineering/book/01-prerequisites/about-your-app/#consumer-versus-b2b) (статья)

### Рассуждающие модели (Reasoning Models)
Источник: [узел "Reasoning Models" на roadmap.sh](https://roadmap.sh/inference-engineering/reasoning-models@Y9YkcfblXHEvS-gdEWwaE)

Рассуждающие модели перед финальным ответом генерируют промежуточную последовательность размышлений: к входу и выходу добавляется третья последовательность токенов. Эта трасса рассуждений заметно увеличивает общее число токенов и меняет экономику инференса: TTFT выше, общая задержка дольше, а стоимость выходных токенов доминирует. Инженерам по инференсу нужно учитывать переменные и порой очень длинные последовательности рассуждений при расчёте инфраструктуры и бюджетов задержки.

Ресурсы:
- [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903) (статья)
- [What is a reasoning model?](https://www.ibm.com/think/topics/reasoning-model) (статья)
- [What Are Large Reasoning Models (LRMs)? Smarter AI Beyond LLMs](https://www.youtube.com/watch?v=enLbj0igyx4) (видео)
- [How do thinking and reasoning models work?](https://www.youtube.com/watch?v=xCRvOUykOX0) (видео)

## Стратегия работы с моделями (Model Strategy)

### Выбор модели (Model Selection)
Источник: [узел "Model Selection" на roadmap.sh](https://roadmap.sh/inference-engineering/model-selection@jQAWZ1plw4_wPE1UvE_Ux)

Самое важное решение в оптимизации производительности модели: какую модель использовать. Модели поменьше, с меньшим числом параметров, быстрее и дешевле в сервинге, чем крупные. Цель: найти самую маленькую модель, которая соответствует требованиям к качеству для задачи. Архитектура модели также определяет, какие движки инференса и техники оптимизации доступны, поэтому предпочтительнее популярные архитектуры с широкой поддержкой инструментов.

Ресурсы:
- [Choosing the Right Model](https://bentoml.com/llm/getting-started/choosing-the-right-model) (статья)
- [Beyond Vibes: How to Properly Select the Right LLM for the Right Task](https://aws.amazon.com/blogs/machine-learning/beyond-vibes-how-to-properly-select-the-right-llm-for-the-right-task/) (статья)
- [How to Pick the Right AI Foundation Model](https://www.youtube.com/watch?v=pePAAGfh-IU) (видео)
- [How to Choose Large Language Models: A Developer’s Guide to LLMs](https://www.youtube.com/watch?v=pYax2rupKEY) (видео)

### Оценка качества модели (Model Evaluation)
Источник: [узел "Model Evaluation" на roadmap.sh](https://roadmap.sh/inference-engineering/model-evaluation@lVf5GoJF_PVTkTiQFTNVg)

Оценка качества модели, или evals, это практика систематического измерения качества модели на конкретной задаче или в конкретной области. Стандартные бенчмарки интеллекта вроде MMLU измеряют общие способности, но их можно обыграть; продуктовые оценки качества, которые проверяют реальные сценарии, дают более надёжный сигнал. Надёжные оценки качества: обязательное условие перед вложениями в оптимизацию инференса: они подтверждают, что модель действительно полезна, прежде чем её ускорять.

Ресурсы:
- [LLM Evaluation: A Beginner's Guide](https://www.evidentlyai.com/llm-guide/llm-evaluation) (статья)
- [LLM Evaluation Metrics and Methods, Explained Simply](https://www.evidentlyai.com/llm-guide/llm-evaluation-metrics) (статья)
- [Automated Regression Testing: The Complete 2026 Guide](https://roadmap.sh/ai-engineer/automated-regression-testing) (статья)
- [LLM as a Judge: Scaling AI Evaluation Strategies](https://www.youtube.com/watch?v=trfUBIDeI1Y) (видео)

### Дообучение (Fine-Tuning)
Источник: [узел "Fine-Tuning" на roadmap.sh](https://roadmap.sh/inference-engineering/fine-tuning@fWJplrAuUStEMNNLQc75G)

Дообучение (fine-tuning) берёт предобученную фундаментальную модель и адаптирует её под конкретную область, обучая на дополнительных размеченных данных. Небольшая дообученная модель может сравняться с гораздо более крупной универсальной на узких задачах вроде text-to-SQL. Модели поменьше быстрее и дешевле в сервинге, поэтому дообучение: один из самых эффективных инструментов для достижения целей по задержке и стоимости.

Ресурсы:
- [What is Fine-Tuning?](https://www.ibm.com/think/topics/fine-tuning) (статья)
- [How I Fine-Tuned Granite-Vision 2B to Beat a 90B Model](https://towardsdatascience.com/how-i-fine-tuned-granite-vision-2b-to-beat-a-90b-model-insights-and-lessons-learned/?utm_source=roadmap&utm_medium=Referral&utm_campaign=TDS+roadmap+integration) (статья)
- [Is Fine-Tuning Still Needed? LLMs, RAG, & LoRA](https://www.youtube.com/watch?v=-W2JdSl1v48) (видео)

### Дистилляция (Distillation)
Источник: [узел "Distillation" на roadmap.sh](https://roadmap.sh/inference-engineering/distillation@IdNkeL9pzy4lFv17ak1Vy)

Дистилляция обучает меньшую модель-ученика подражать большей модели-учителю, показывая ей распределения вероятностей учителя, а не только его финальные ответы. В отличие от дообучения на синтетических данных, дистилляция передаёт поведение учителя при рассуждении. Полученная модель-ученик меньше и быстрее, при этом сохраняет большую часть качества учителя на тех же задачах.

Ресурсы:
- [Adversarial Diffusion Distillation](https://arxiv.org/abs/2311.17042) (статья)
- [How Knowledge Distillation Works and When to Use It](https://www.arcee.ai/blog/how-knowledge-distillation-works-and-when-to-use-it) (статья)
- [Introduction to model distillation: Efficient knowledge transfer for AI applications](https://nebius.com/blog/posts/model-distillation-intro) (статья)
- [Model Distillation: How to Steal a Billion-Dollar AI](https://www.youtube.com/watch?v=QBG6bXiOq40) (видео)
- [Knowledge Distillation - Explained](https://www.youtube.com/watch?v=Pwo1bLDB-jA) (видео)
