# Введение (Introduction)

## Инженер по инференсу (Inference Engineer)
Источник: [узел "Introduction" на roadmap.sh](https://roadmap.sh/inference-engineering/introduction@GL-9aJKTJT9s4maeT37Uf)

Инженерия инференса это практика, которая делает сервинг генеративных ИИ-моделей в продакшене быстрее, дешевле и надёжнее. Она охватывает весь стек: от CUDA-ядер и архитектуры GPU до автомасштабирования в Kubernetes и управления мощностями в нескольких облаках. Область сложилась вместе со взрывным ростом открытых моделей и переходом от API с оплатой за токен к выделенным развёртываниям, где инженеры напрямую отвечают за задержку, пропускную способность, стоимость и аптайм.

Ресурсы:
- [Inference Engineering](https://www.baseten.co/inference-engineering/digital-download/) (книга)
- [What Is Inference Engineering? The 2026 GPU Cloud Guide](https://www.spheron.network/blog/inference-engineering-guide-2026/) (статья)
- [A Guide to AI Inference Engineering](https://blog.bytebytego.com/p/a-guide-to-ai-inference-engineering) (статья)
- [AI Inference: The Secret to AI's Superpowers](https://www.youtube.com/watch?v=XtT5i0ZeHHE&t=19s) (видео)

### Открытые и закрытые модели (Open vs. Closed Models)
Источник: [узел "Open vs Closed Models" на roadmap.sh](https://roadmap.sh/inference-engineering/open-vs-closed-models@KAt5FzglOUtH7jLlzDn-I)

К закрытым моделям доступ есть только через API вендора; их веса никогда не публикуются. Открытые модели выкладывают веса для скачивания и самостоятельного хостинга. Для инженера по инференсу это различие задаёт всё пространство задач: закрытые модели не требуют инфраструктуры, но не дают контроля над задержкой, стоимостью и конфигурацией, а открытые требуют построить и эксплуатировать полный стек инференса, зато дают полный контроль над каждым его слоем.

Ресурсы:
- [AI Engineering: Building Applications with Foundation Models](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) (книга)
- [Open-source Models vs. Closed-Source Models: A Simple Guide](https://koat.ai/blog/open-source-models-vs-closed-source-models-a-simple-guide) (статья)
- [Open-Source vs. Closed LLMs: A Guide](https://hatchworks.com/blog/gen-ai/open-source-vs-closed-llms-guide/) (статья)
- [Open Source vs Closed AI: LLMs, Agents & the AI Stack Explained](https://www.youtube.com/watch?v=_QfxGZGITGw) (видео)

### Инференс и обучение (Inference vs. Training)
Источник: [узел "Inference vs. Training" на roadmap.sh](https://roadmap.sh/inference-engineering/inference-vs-training@fVUfQYb8BP_hFMmd1S2-J)

Обучение это подбор весов модели по данным. Инференс это сервинг этих весов в продакшене для генерации ответов. Запуски обучения это вычислительно тяжёлые батч-задания; инференс же работает как непрерывный сервис, чувствительный к задержке. Успех обучения измеряют кривыми функции потерь, успех инференса: временем до первого токена, токенами в секунду и аптаймом.

Ресурсы:
- [Language Models Are Few-Shot Learners](https://arxiv.org/abs/2005.14165) (статья)
- [Inference vs Training](https://www.cloudflare.com/learning/ai/inference-vs-training/) (статья)
- [What is Machine Learning Inference?](https://hazelcast.com/glossary/machine-learning-inference/) (статья)
- [Why Inference is hard..](https://www.youtube.com/watch?v=B18zBnjZKmc) (видео)

### Общий и выделенный инференс (Shared vs. Dedicated Inference)
Источник: [узел "Shared vs. Dedicated Inf." на roadmap.sh](https://roadmap.sh/inference-engineering/shared-vs-dedicated-inf@2DsjfW9r4dOI3LDQU80qt)

Общий инференс это отправка запросов в публичный API с оплатой за токен. Выделенный инференс это аренда GPU и запуск собственного сервера модели с оплатой за GPU-час. Общий инференс проще и не имеет холодного старта, зато выделенный даёт контроль над задержкой, стоимостью при масштабировании, кастомизацией модели и аптаймом. Большинство продуктов начинают с общего инференса и переходят на выделенный по мере роста трафика.

Ресурсы:
- [Dedicated vs shared LLM inference: when reserved capacity makes sense](https://www.freestyle.sh/blog/engineering/dedicated-vs-shared-llm-inference) (статья)
- [Serverless vs. Self-Hosted LLM Inference](https://bentoml.com/llm/llm-inference-basics/serverless-vs-self-hosted-llm-inference) (статья)
- [Self-Hosted LLM: A Practical Guide for DevOps](https://www.plural.sh/blog/self-hosting-large-language-models/) (статья)
- [When shared inference is not enough: the case for dedicated AI endpoints](https://www.gmicloud.ai/en/blog/when-shared-inference-is-not-enough-the-case-for-dedicated-ai-endpoints) (статья)

### Стек инференса (The Inference Stack)
Источник: [узел "The Inference Stack" на roadmap.sh](https://roadmap.sh/inference-engineering/the-inference-stack@uIhVVlMsykuxJCa02f-i-)

Полная система инференса состоит из трёх слоёв: рантайм, инфраструктура и инструменты. Слой рантайма оптимизирует одну модель на одном инстансе с помощью батчинга, кеширования, квантования и спекулятивного декодирования. Слой инфраструктуры масштабирует систему по кластерам, регионам и облачным провайдерам, сохраняя аптайм. Слой инструментов даёт инженерам подходящий уровень абстракции, чтобы продуктивно управлять системой. Для критически важного инференса в масштабе все три слоя должны работать вместе.
