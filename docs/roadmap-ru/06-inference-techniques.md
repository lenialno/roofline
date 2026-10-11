# Техники инференса (Inference Techniques)

## Квантование (Quantization)
Источник: [узел "Quantization" на roadmap.sh](https://roadmap.sh/inference-engineering/quantization@DaSqcLHfnJ4_n9utVVTSk)

Квантование переводит веса модели и другие значения из их исходной точности в формат меньшей точности. Уменьшение точности вдвое удваивает пропускную способность памяти для фазы decode и даёт вдвое больше FLOPS для фазы prefill на совместимых Tensor Core. Обратная сторона: возможная потеря качества из-за сниженной численной точности, которая может накапливаться по множеству вычислений в прямом проходе.

Ресурсы:
- [AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration](https://github.com/mit-han-lab/llm-awq) (исходный код)
- [bitsandbytes](https://github.com/TimDettmers/bitsandbytes) (исходный код)
- [SmoothQuant](https://github.com/mit-han-lab/smoothquant) (исходный код)
- [What is quantization?](https://www.ibm.com/think/topics/quantization) (статья)
- [How LLMs survive in low precision | Quantization Fundamentals](https://www.youtube.com/watch?v=qoQJq5UwV1c) (видео)

### Квантование после обучения (Post-Training Quantization)
Источник: [узел "Post-Training Quantization" на roadmap.sh](https://roadmap.sh/inference-engineering/post-training-quantization@Zvvs8cB98IRee1okBILsS)

Квантование после обучения (PTQ) переводит веса готовой модели в меньшую точность уже после завершения обучения. Для этого используют небольшой калибровочный набор данных, по которому вычисляют послойные масштабные коэффициенты, минимизирующие разрыв между выходами квантованной и исходной модели. Это стандартный подход для большинства развёртываний, поскольку он не требует переобучения и применим к любой существующей модели. Ведущим инструментом остаётся NVIDIA ModelOpt: он экспортирует квантованные модели в форматы, совместимые со всеми основными движками инференса.

Ресурсы:
- [AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration](https://github.com/mit-han-lab/llm-awq) (исходный код)
- [bitsandbytes](https://github.com/TimDettmers/bitsandbytes) (исходный код)
- [SmoothQuant](https://github.com/mit-han-lab/smoothquant) (исходный код)
- [Optimizing LLMs for Performance and Accuracy with Post-Training Quantization](https://developer.nvidia.com/blog/optimizing-llms-for-performance-and-accuracy-with-post-training-quantization/) (статья)
- [Post-training quantization](https://developers.google.com/edge/litert/conversion/tensorflow/quantization/post_training_quantization) (статья)
- [Reverse-engineering GGUF | Post-Training Quantization](https://www.youtube.com/watch?v=vW30o4U9BFE) (статья)

### Обучение с учётом квантования (Quantization-Aware Training)
Источник: [узел "Quantization-Aware Training" на roadmap.sh](https://roadmap.sh/inference-engineering/quantization-aware-training@QCXV4Utq0Ajs1krLM3fhg)

Обучение с учётом квантования (QAT) вычисляет масштабные коэффициенты и оптимизирует веса модели совместно в ходе обучения, так что итоговая модель уже откалибрована под целевой формат низкой точности. Это даёт лучшее качество при низкой точности, чем квантование после обучения, но требует переобучения модели с нуля или с чекпоинта. Некоторые лаборатории выпускают модели, обученные таким способом, например GPT-OSS в MXFP4.

Ресурсы:
- [What is quantization aware training?](https://www.ibm.com/think/topics/quantization-aware-training) (статья)
- [How Quantization Aware Training Enables Low-Precision Accuracy Recovery](https://developer.nvidia.com/blog/how-quantization-aware-training-enables-low-precision-accuracy-recovery/) (статья)
- [Quantization Aware Training (QAT) With a Custom DataLoader](https://www.youtube.com/watch?v=s3tqqBaRuHE) (видео)

### ModelOpt
Источник: [узел "ModelOpt" на roadmap.sh](https://roadmap.sh/inference-engineering/modelopt@zhiKpdZm8zOg4e3bm1OgN)

ModelOpt, набор инструментов NVIDIA для квантования после обучения, поддерживает выходные форматы FP8, INT8, FP4, MXFP8, MXFP4 и NVFP4. Он интегрируется с PyTorch и экспортирует квантованные модели напрямую в TensorRT-LLM, vLLM и SGLang. Калибровка прогоняет через модель небольшой набор репрезентативных входов, чтобы вычислить послойные масштабные коэффициенты, минимизирующие разрыв между выходами квантованной и исходной модели.

Ресурсы:
- [Optimize Models with NVIDIA Model Optimizer](https://www.jetson-ai-lab.com/tutorials/modelopt-on-jetson/) (официальная документация)
- [Model Quantization: Post-Training Quantization Using NVIDIA Model Optimizer](https://developer.nvidia.com/blog/model-quantization-post-training-quantization-using-nvidia-model-optimizer/) (официальная документация)
- [Model-Optimizer](https://github.com/NVIDIA/Model-Optimizer) (исходный код)
- [NVIDIA ModelOpt](https://huggingface.co/docs/diffusers/en/quantization/modelopt) (статья)

### Измерение влияния на качество (Measuring Quality Impact)
Источник: [узел "Measuring Quality Impact" на roadmap.sh](https://roadmap.sh/inference-engineering/measuring-quality-impact@mK_4R8liXtl64iG7ONvgz)

После квантования качество модели нужно проверить относительно оригинала. Используют три метода: оценку перплексии (чем ниже, тем лучше; после квантования рост должен быть минимальным), стандартные бенчмарки интеллекта вроде MMLU или SWE-bench и продуктовые evals, подогнанные под реальный сценарий использования. Все три должны показывать различия, неотличимые от шума, прежде чем квантованную модель можно выпускать в эксплуатацию.

Ресурсы:
- [Perplexity for LLM Evaluation](https://www.comet.com/site/blog/perplexity-for-llm-evaluation/) (статья)
- [AI Benchmarks Explained: MMLU, ARC-AGI, and SWE-bench](https://lumichats.com/blog/ai-benchmarks-explained-mmlu-arc-agi-swe-bench-2026) (статья)
- [What is perplexity?](https://www.youtube.com/watch?v=NURcDHhYe98&t=10s) (видео)
- [What do AI Benchmarks Actually Mean?! A Fast Breakdown (MMLU, SWE-bench, & More Explained)](https://www.youtube.com/watch?v=fSWg4HAJjBo) (видео)

## Спекулятивное декодирование (Speculative Decoding)
Источник: [узел "Speculative Decoding" на roadmap.sh](https://roadmap.sh/inference-engineering/speculative-decoding@gMWgd10cxcQG_RG2oSAEH)

Спекулятивное декодирование использует свободные вычислительные ресурсы во время фазы decode, которая ограничена пропускной способностью памяти: оно генерирует несколько черновых токенов и проверяет их за один прямой проход. Если целевая модель принимает N черновых токенов, прямой проход даёт N+1 токенов вместо одного. Выигрыш в производительности зависит от стоимости черновых токенов, длины черновой последовательности и доли принятых токенов, которая падает при более высокой температуре и больших размерах батча.

Ресурсы:
- [An Introduction to Speculative Decoding for Reducing Latency in AI Inference](https://developer.nvidia.com/blog/an-introduction-to-speculative-decoding-for-reducing-latency-in-ai-inference/) (статья)
- [Speculative Decoding - vLLM](https://docs.vllm.ai/en/latest/features/speculative_decoding/) (статья)
- [Fast Inference from Transformers via Speculative Decoding](https://arxiv.org/abs/2211.17192) (статья)
- [Faster LLMs: Accelerate Inference with Speculative Decoding](https://www.youtube.com/watch?v=VkWlLSTdHs8) (видео)
- [Speculative Decoding: When Two LLMs are Faster than One](https://www.youtube.com/watch?v=S-8yr_RibJ4) (видео)

### Спекулятивное декодирование с черновой и целевой моделью (Draft-Target Speculative Decoding)
Источник: [узел "Draft-Target Decoding" на roadmap.sh](https://roadmap.sh/inference-engineering/draft-target-decoding@m0EIHovHWGkWULN0a3C3v)

Спекуляция по схеме "черновая и целевая модель" использует небольшую черновую модель, обычно как минимум в десять раз меньше целевой, чтобы генерировать черновые токены, которые целевая модель затем проверяет. Черновая модель должна использовать тот же токенизатор и в целом вести себя так же, как целевая; часто это младшая модель того же семейства. Это самый простой в настройке метод спекуляции, но он даёт наибольшие накладные расходы, поскольку запускает отдельную модель.

Ресурсы:
- [Fast Inference from Transformers via Speculative Decoding](https://arxiv.org/abs/2211.17192) (статья)
- [An Introduction to Speculative Decoding for Reducing Latency in AI Inference](https://developer.nvidia.com/blog/an-introduction-to-speculative-decoding-for-reducing-latency-in-ai-inference/) (статья)
- [Draft-Target Speculative Decoding Simulation](https://www.deep-ml.com/problems/430) (статья)

### EAGLE
Источник: [узел "EAGLE" на roadmap.sh](https://roadmap.sh/inference-engineering/eagle@0FZTg3_ZnTpMOQ078OOxE)

В EAGLE, специально разработанном методе спекуляции, небольшую черновую модель обучают принимать на вход скрытые состояния целевой модели. Благодаря доступу к внутренним представлениям целевой модели EAGLE достигает более высокой доли принятых токенов и более длинных черновых последовательностей (до восьми токенов), чем универсальная маленькая модель. Он встраивается в тот же прямой проход, что и целевая модель, и убирает накладные расходы на оркестрацию раздельных запусков черновой и целевой моделей.

Ресурсы:
- [EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty](https://arxiv.org/abs/2401.15077) (статья)
- [EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees](https://arxiv.org/abs/2406.16858) (статья)
- [EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test](https://arxiv.org/abs/2503.01840) (статья)
- [EAGLE and EAGLE-2: Lossless Inference Acceleration for LLMs - Hongyang Zhang](https://www.youtube.com/watch?v=oXRSorx-Llg) (видео)
- [Speculative Decoding, Explained: Why EAGLE-3 Finally Scales | 20-Min Deep Dive](https://www.youtube.com/watch?v=aXdQ3JbRb98) (видео)

### N-граммная спекуляция (N-gram Speculation)
Источник: [узел "N-gram" на roadmap.sh](https://roadmap.sh/inference-engineering/n-gram@ZOclQMd7JASGXTRyctfW2)

N-граммная спекуляция строит во время фазы prefill словарь, который сопоставляет префиксам токенов продолжения n-грамм, встреченные во входе. Во время фазы decode сгенерированные токены ищутся в этом словаре, и совпавшие суффиксы становятся черновыми токенами; отдельная модель не нужна. Метод наиболее эффективен для дополнения кода, где вывод часто повторяет синтаксис входа, и в этой области может давать очень длинные черновые последовательности с высокой долей принятых токенов.

Ресурсы:
- [Introducing N-gram Speculative Decoding: Faster Inference for Structured Tasks](https://friendli.ai/blog/n-gram-speculative-decoding) (статья)
- [What is N-gram Speculation in LLMs and How Does It Speed Up Generation?](https://outcomeschool.com/blog/n-gram-speculation-in-llms) (статья)
- [Break the Sequential Dependency of LLM Inference Using Lookahead Decoding](https://arxiv.org/abs/2402.02057) (статья)

## Кеширование (Caching)
Источник: [узел "Caching" на roadmap.sh](https://roadmap.sh/inference-engineering/caching@PzEj5yq1lDQ324RWYpDdQ)

Кеширование переиспользует ранее вычисленные значения KV, чтобы не повторять вычисления prefill для запросов с общим контекстом. Это одна из самых результативных техник снижения TTFT в нагрузках с длинными системными промптами или многоходовыми диалогами. Эта группа охватывает подходы, уровни хранения, последствия для маршрутизации и стратегии работы с длинным контекстом, которые делают кеширование эффективным в масштабе.

Ресурсы:
- [KV Caching Explained: Optimizing Transformer Inference Efficiency](https://huggingface.co/blog/not-lain/kv-caching) (статья)
- [KV Caching in LLMs: A Guide for Developers](https://machinelearningmastery.com/kv-caching-in-llms-a-guide-for-developers/) (статья)
- [KV Cache: The Trick That Makes LLMs Faster](https://www.youtube.com/watch?v=gpp57x_z_Jg) (видео)
- [The KV Cache: Memory Usage in Transformers](https://www.youtube.com/watch?v=80bIUggRJf4&t=247s) (видео)

### Подходы к кешированию (Caching Approaches)
Источник: [узел "Caching Approaches" на roadmap.sh](https://roadmap.sh/inference-engineering/caching-approaches@2nGv7_8PTWYr7uqbudCcX)

Переиспользование KV-кеша остаётся основной стратегией кеширования в инференсе LLM и включает префиксное кеширование (переиспользование закешированных значений KV между запросами с общим префиксом) и выгрузку KV-кеша (перенос редко используемых блоков кеша на более медленные уровни хранения, чтобы освободить VRAM GPU). С этим связана маршрутизация с учётом кеша: она направляет запросы на реплики, у которых нужный закешированный префикс скорее всего уже есть.

Ресурсы:
- [LMCache](https://github.com/LMCache/LMCache) (исходный код)
- [What is Prompt Caching?](https://www.ibm.com/think/topics/prompt-caching) (статья)
- [What is Prompt Caching? Optimize LLM Latency with AI Transformers](https://www.youtube.com/watch?v=u57EnkQaUTY) (видео)
- [How KV Cache Speeds Up LLMs for Faster AI Models on GPUs](https://www.youtube.com/watch?v=o0gkdZBtwEg&t=1s) (видео)

### Хранение KV-кеша (KV Cache Storage)
Источник: [узел "KV Cache Storage" на roadmap.sh](https://roadmap.sh/inference-engineering/kv-cache-storage@gkt2Gr34RJJf1NZgbmtXf)

KV-кеши можно хранить в VRAM GPU (быстрее всего, десятки и сотни гигабайт), в оперативной памяти CPU (медленнее, сотни гигабайт и терабайты), на локальном SSD или на сетевом SSD. Перенос реже используемых блоков KV на более медленное хранилище освобождает VRAM для активных запросов. KV Block Manager в NVIDIA Dynamo даёт API для прозрачного управления блоками KV между этими уровнями хранения.

Ресурсы:
- [LMCache](https://github.com/LMCache/LMCache) (исходный код)
- [KV Cache Storage Is the New AI Inference Bottleneck](https://xinnor.io/blog/kv-cache-storage-is-the-new-ai-inference-bottleneck-how-lustre-ro-pcc-and-xiraid-make-shared-storage-competitive-with-local-nvme-for-long-context-llm-serving/) (статья)
- [Stop Calling It KV Cache: It’s Something Much Bigger](https://blog.lmcache.ai/en/2026/04/28/stop-calling-it-kv-cache-its-something-much-bigger/) (статья)
- [CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion](https://arxiv.org/abs/2405.16444) (статья)

### Маршрутизация с учётом кеша (Cache-Aware Routing)
Источник: [узел "Cache-Aware Routing" на roadmap.sh](https://roadmap.sh/inference-engineering/cache-aware-routing@3DR0Qvqu2qUTi9niU_63n)

В развёртываниях с несколькими репликами маршрутизация с учётом кеша направляет запрос на реплику, у которой подходящий префикс скорее всего уже лежит в KV-кеше. Без этого пользователь в длинном диалоге может на каждом ходу попадать на разные реплики и получать промахи кеша, которые увеличивают задержку. Глобальный KV-кеш на сетевом SSD позволяет всем репликам со временем получить доступ к любой закешированной последовательности.

Ресурсы:
- [Why Agentic Inference Needs Prefix-Aware Routing Infrastructure](https://www.coreweave.com/blog/why-agentic-inference-needs-prefix-aware-routing-infrastructure) (статья)
- [Enabling inference at massive scale with hybrid storage for KV cache offloading.](https://www.seagate.com/es/es/resources/enabling-inference-at-massive-scale-with-hybrid-storage-for-kv-cache-offloading/) (статья)
- [KV Cache Aware Routing](https://docs.vllm.ai/projects/production-stack/en/vllm-stack-0.1.5/tutorials/kvaware.html) (статья)
- [Prefix-Cache Aware Routing](https://llm-d.ai/docs/architecture/advanced/kv-management/prefix-cache-aware-routing) (статья)

### Работа с длинным контекстом (Long Context Handling)
Источник: [узел "Long Context Handling" на roadmap.sh](https://roadmap.sh/inference-engineering/long-context-handling@uL3Fn8XfS1Yv_PJd9R8wi)

Длинные последовательности создают KV-кеши такого размера, что они нагружают память GPU, замедляют decode и увеличивают время prefill. Техники работы с длинным контекстом: FlashAttention для вычисления внимания с экономией памяти, PagedAttention для хранения KV в несмежных блоках, chunked prefill для чередования длинного prefill с decode и подходы на уровне модели вроде скользящего окна внимания, которое ограничивает, на сколько предыдущих токенов смотрит каждый токен.

Ресурсы:
- [Ring Attention with Blockwise Transformers for Near-Infinite Context](https://arxiv.org/abs/2310.01889) (статья)
- [RoFormer: Enhanced Transformer with Rotary Position Embedding](https://arxiv.org/abs/2104.09864) (статья)
- [What is Long Context and Why Does it Matter for AI?](https://cloud.google.com/transform/the-prompt-what-are-long-context-windows-and-why-do-they-matter) (статья)
- [Long-Context LLM Infrastructure: Building Systems for Million-Token Windows](https://introl.com/blog/long-context-llm-infrastructure-million-token-windows-guide) (статья)
- [Deep Dive into Long Context](https://www.youtube.com/watch?v=NHMJ9mqKeMQ) (видео)

## Параллелизм моделей (Model Parallelism)
Источник: [узел "Model Parallelism" на roadmap.sh](https://roadmap.sh/inference-engineering/model-parallelism@CiXsdHHL0e2DN4ICI5jeX)

Когда модель не помещается на один GPU или когда для нужной задержки сервинга требуется больше вычислений, чем может дать одно устройство, параллелизм моделей распределяет нагрузку по нескольким GPU или узлам. Эта группа охватывает три стратегии параллелизма и их компромиссы по накладным расходам на коммуникацию, задержке и требованиям к оборудованию.

Ресурсы:
- [Model Parallelism](https://huggingface.co/docs/transformers/v4.13.0/en/parallelism) (статья)
- [LLM Model Parallelism](https://www.youtube.com/watch?v=DryXbg48bLc) (видео)
- [How LLMs use multiple GPUs](https://www.youtube.com/watch?v=4i76hmmnJEo) (видео)

### Тензорный параллелизм (Tensor Parallelism)
Источник: [узел "Tensor Parallelism" на roadmap.sh](https://roadmap.sh/inference-engineering/tensor-parallelism@csghcNLDywO8oTIZNXeyP)

Тензорный параллелизм (TP) разрезает матрицы весов каждого слоя между несколькими GPU и распределяет матричное умножение. Каждый GPU обрабатывает свой шард каждого слоя, а результаты объединяются операцией all-reduce перед следующим слоем. Он снижает задержку для отдельного пользователя, деля между GPU и VRAM, и вычисления, но требует быстрых соединений NVLink и плохо подходит для многоузловых развёртываний.

Ресурсы:
- [NVIDIA/Megatron-LM](https://github.com/NVIDIA/Megatron-LM) (исходный код)
- [Tensor Parallelism](https://huggingface.co/docs/text-generation-inference/en/conceptual/tensor_parallelism) (статья)
- [Demystifying Tensor Parallelism](https://robotchinwag.com/posts/demystifying-tensor-parallelism/) (статья)
- [What Is Tensor Parallelism and How to Apply It](https://www.newline.co/@Dipen/what-is-tensor-parallelism-and-how-to-apply-it--b4633fa4) (статья)

### Конвейерный параллелизм (Pipeline Parallelism)
Источник: [узел "Pipeline Parallelism" на roadmap.sh](https://roadmap.sh/inference-engineering/pipeline-parallelism@9KLS3gWArBofLEULu3sQc)

Конвейерный параллелизм (PP) делит слои LLM на последовательные стадии и назначает каждую стадию отдельному GPU или узлу. В отличие от тензорного параллелизма каждый GPU хранит целые слои, а не их фрагменты. Он создаёт конвейерные пузыри (pipeline bubbles), когда GPU ждут предыдущие стадии, и это снижает эффективность. Применяется для многоузлового инференса плотных моделей, обычно в сочетании с тензорным параллелизмом внутри каждого узла.

Ресурсы:
- [NVIDIA/Megatron-LM](https://github.com/NVIDIA/Megatron-LM) (исходный код)
- [LLM Training - Fundamentals of Pipeline Parallelism](https://medium.com/byte-sized-ai/pipeline-parallelism-explained-in-2-mins-6bdf1ab29053) (статья)
- [Pipeline Parallelism](https://docs.pytorch.org/docs/2.14/distributed.pipelining.html) (статья)
- [What Is Pipeline Parallelism and How to Use It](https://www.newline.co/@Dipen/what-is-pipeline-parallelism-and-how-to-use-it--8db3dd11) (статья)

### Экспертный параллелизм (Expert Parallelism)
Источник: [узел "Expert Parallelism" на roadmap.sh](https://roadmap.sh/inference-engineering/expert-parallelism@62y78y-RXZT_QCUfd-YFE)

Экспертный параллелизм (EP) распределяет экспертов MoE между GPU так, что каждый GPU содержит несколько целых экспертов. Токены направляются на тот GPU, где находятся их активированные эксперты, и каждый эксперт выполняется независимо в пределах одного GPU, без разрезания на несколько. У EP ниже накладные расходы на обмен между GPU, чем у тензорного параллелизма, и он хорошо масштабируется на многоузловые развёртывания через InfiniBand.

Ресурсы:
- [Expert parallelism](https://huggingface.co/docs/transformers/en/expert_parallelism) (статья)
- [Expert Parallelism: Scaling Mixture-of-Experts Models](https://www.digitalocean.com/community/tutorials/expert-parallelism-in-deep-learning) (статья)
- [Expert Parallelism: Distributing Experts Across Devices](https://apxml.com/courses/mixture-of-experts/chapter-4-scaling-moe-distributed-training/expert-parallelism-moe) (статья)

### Многоузловой инференс (Multi-Node Inference)
Источник: [узел "Multi-Node Inference" на roadmap.sh](https://roadmap.sh/inference-engineering/multi-node-inference@FZx2xsqw_cmYLFS3GMAl-)

Многоузловой инференс распределяет модель более чем на восемь GPU, используя InfiniBand для связи между узлами. Он необходим для самых больших моделей, когда одному узлу не хватает VRAM на веса и KV-кеш. Пропускная способность InfiniBand на порядок ниже, чем у NVLink, поэтому стратегии параллелизма должны сводить межузловую коммуникацию к минимуму. Для MoE-моделей между узлами предпочтителен экспертный параллелизм, а не тензорный.

Ресурсы:
- [How multi-node inference works for massive LLMs like DeepSeek-R1](https://www.baseten.co/blog/how-multi-node-inference-works-llms-deepseek-r1/#from-single-node-to-multi-node-infrastructure) (статья)
- [AI Models Are Huge, but Your GPUs Aren’t: Mastering Multi-Node Distributed Inference](https://www.youtube.com/watch?v=MQR8jyTR5QE&xstg=CAMSEBUJ_b-oH-PhF0yjBgb_zzE%3D) (видео)

## Дезагрегация prefill и decode (Disaggregation)
Источник: [узел "Disaggregation" на roadmap.sh](https://roadmap.sh/inference-engineering/disaggregation@f6PWIqf4LubR7lQztaoB5)

Дезагрегация разносит фазы prefill и decode на независимые GPU-инстансы, которые можно масштабировать отдельно. Движок prefill обрабатывает входную последовательность и передаёт полученный KV-кеш движку decode через аппаратное соединение. Это убирает конкуренцию за ресурсы между prefill, тяжёлым по вычислениям, и decode, тяжёлым по памяти. Дезагрегация наиболее эффективна при большом трафике, для крупных моделей и при нагрузках с преобладанием prefill, таких как редакторы кода.

Ресурсы:
- [Beyond the Buzz: A Pragmatic Take on Inference Disaggregation](https://arxiv.org/abs/2506.05508) (статья)
- [Disaggregated Serving](https://llm-d.ai/docs/architecture/advanced/disaggregation) (статья)
- [Disaggregated Serving in LLM Inference, Explained](https://handbook.modular.com/inference-optimization/prefill-decode-disaggregation/) (статья)
- [Why Separating Prefill and Decode Makes LLMs Faster | vLLM, LLM-D and NIXL](https://www.youtube.com/watch?v=BaD3CTYf6V0) (видео)

### NVIDIA Dynamo
Источник: [узел "NVIDIA Dynamo" на roadmap.sh](https://roadmap.sh/inference-engineering/nvidia-dynamo@KhTFecXEkHR4WX-_TYY3g)

Dynamo поддерживает условную дезагрегацию: запросы сначала отправляются в движок decode и направляются в движок prefill только тогда, когда вход длинный или ещё не закеширован. Соотношение движков prefill и decode настраивается во время работы и может меняться вместе с паттернами трафика. Такое динамическое распределение не даёт очереди prefill стать узким местом и не тратит ресурсы движка decode впустую на трафик с преобладанием prefill.

Ресурсы:
- [NVIDIA Dynamo Documentation](https://docs.nvidia.com/dynamo/latest/index.html) (официальная документация)
- [Disaggregated Serving](https://docs.nvidia.com/dynamo/kubernetes/disaggregated-serving/overview) (официальная документация)
- [NVIDIA Dynamo 1.0: Disaggregated LLM Inference Deployment Guide (2026)](https://www.spheron.network/blog/nvidia-dynamo-disaggregated-inference-guide/) (статья)
- [NVIDIA Dynamo in 5 Minutes: What Is It and Why Now?](https://www.youtube.com/watch?v=mXYFcz27eDw&t=7s) (видео)
