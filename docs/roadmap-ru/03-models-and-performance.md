# Модели и производительность (Models & Performance)

## Нейронные сети (Neural Networks)
Источник: [узел "Neural Networks" на roadmap.sh](https://roadmap.sh/inference-engineering/neural-networks@p2S0W3EDn768jbqzc7CE7)

Нейронной сетью называют многослойную структуру из узлов, где каждый узел применяет к своему входу обученную матрицу весов и смещение. Несколько слоёв, соединённых последовательно, образуют основу всех генеративных моделей ИИ. Инженеру инференса нужно рабочее понимание того, как нейронные сети вычисляют выход, чтобы видеть, где возникают узкие места производительности.

Ресурсы:
- [Deep Learning](https://www.deeplearningbook.org/) (книга)
- [Deep Learning with Python](https://www.manning.com/books/deep-learning-with-python-second-edition) (книга)
- [What is deep learning?](https://www.ibm.com/think/topics/deep-learning) (статья)
- [But what is a neural network?](https://www.youtube.com/watch?v=aircAruvnKk) (видео)

### Архитектуры энкодер-декодер (Encoder-Decoder Architectures)
Источник: [узел "Encoder-Decoder Arch." на roadmap.sh](https://roadmap.sh/inference-engineering/encoder-decoder-arch@nORbxBOAtl9sNU4sIJgP3)

Нейронные сети бывают только с энкодером, только с декодером или типа энкодер-декодер. Современные LLM устроены только с декодером (decoder-only). Модели только с энкодером, такие как BERT, используют для текстовых эмбеддингов и классификации. В моделях энкодер-декодер, таких как Whisper, энкодер переводит вход во внутреннее представление, а декодер авторегрессионно генерирует выходные токены. У каждой архитектуры свои характеристики инференса и свои требования к инструментам.

Ресурсы:
- [Encoder-Decoder Architecture](https://www.skills.google/course_templates/543) (курс)
- [What is an encoder-decoder model?](https://www.ibm.com/think/topics/encoder-decoder-model) (статья)
- [Encoder-decoder architecture: Overview](https://www.youtube.com/watch?v=zbdong_h-x4) (видео)
- [Sequence-to-Sequence (seq2seq) Encoder-Decoder Neural Networks,](https://www.youtube.com/watch?v=L8HKweZIOmg) (видео)

## Большие языковые модели (Large Language Models)
Источник: [узел "Large Language Models" на roadmap.sh](https://roadmap.sh/inference-engineering/large-language-models@irgGvEnY1_WW1EPtuMKgC)

LLM устроена как трансформер только с декодером и состоит из трёх основных компонентов: слоя эмбеддингов, который переводит входные токены в векторы; стека блоков трансформера, которые обрабатывают эти векторы; и выходной головы языкового моделирования, которая превращает финальные скрытые состояния в распределение вероятностей по словарю. Конфигурационный файл открытой модели задаёт все детали архитектуры, включая число слоёв, размерность скрытых состояний и число голов внимания.

Ресурсы:
- [Build a Large Language Model From Scratch](https://dl.tehrandata.org/book/Build-a-large-language-models.pdf) (книга)
- [What is a Large Language Model (LLM)?](https://www.cloudflare.com/en-gb/learning/ai/what-is-large-language-model/) (статья)
- [New to LLMs? Start Here](https://towardsdatascience.com/new-to-llms-start-here/?utm_source=roadmap&utm_medium=Referral&utm_campaign=TDS+roadmap+integration) (статья)
- [How Large Language Models Work](https://www.youtube.com/watch?v=5sLYAQS9sWQ) (видео)

### Блоки трансформера (Transformer Blocks)
Источник: [узел "Transformer Blocks" на roadmap.sh](https://roadmap.sh/inference-engineering/transformer-blocks@xHM7qjigMmXEwxeMEeMWl)

Блоками трансформера называют повторяющиеся скрытые слои LLM. Каждый блок содержит подслой внимания, подслой полносвязной (feed-forward) сети и слои нормализации. В полносвязной сети находится большая часть параметров модели, а внимание остаётся самой вычислительно сложной операцией в расчёте на токен.

Ресурсы:
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) (статья)
- [What Are Transformer Models and How Do They Work?](https://cohere.com/llmu/what-are-transformer-models) (статья)
- [A Simplified Explanation of the Transformer Block](https://medium.com/@akhileshkapse/a-simplified-explanation-of-the-transformer-block-must-read-blog-for-nlp-enthusiasts-12ef240a62ac) (статья)
- [Transformers, the tech behind LLMs](https://www.youtube.com/watch?v=wjZofJX0v4M&t=183s) (видео)

### Механизм внимания (Attention Mechanism)
Источник: [узел "Attention Mechanism" на roadmap.sh](https://roadmap.sh/inference-engineering/attention-mechanism@2KY3T5JVHQBR8pmAiuq0V)

Механизм внимания позволяет трансформерам связывать каждый токен со всеми предыдущими через проекции query, key и value. На фазе decode каждый новый токен обращается ко всем предыдущим токенам, а KV-кеш хранит заранее вычисленные ключи и значения, чтобы не пересчитывать их заново. Внимание остаётся самой дорогой и самой оптимизируемой операцией в инференсе LLM.

Ресурсы:
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) (статья)
- [What is an attention mechanism?](https://www.ibm.com/think/topics/attention-mechanism) (статья)
- [Attention mechanism: Overview](https://www.youtube.com/watch?v=fjJOgb-E41w&t=1s) (видео)
- [Attention in transformers, step-by-step](https://www.youtube.com/watch?v=eMlx5fFNoYc) (видео)

### KV-кеш (KV Cache)
Источник: [узел "KV Cache" на roadmap.sh](https://roadmap.sh/inference-engineering/kv-cache@V678kX8FPChTZCe7Nqwhv)

KV-кеш хранит тензоры ключей и значений, вычисленные в механизме внимания для каждого уже обработанного токена. Без него внимание пересчитывало бы все предыдущие токены на каждом шаге decode, и инференс стал бы недопустимо медленным. KV-кеш живёт в памяти GPU, его размер растёт с длиной последовательности и размером батча, поэтому он главная цель для техник управления памятью.

Ресурсы:
- [Efficient Memory Management for Large Language Model Serving with PagedAttention](https://arxiv.org/abs/2309.06180) (статья)
- [KV Caching Explained: Optimizing Transformer Inference Efficiency](https://huggingface.co/blog/not-lain/kv-caching) (статья)
- [How KV Cache Speeds Up LLMs for Faster AI Models on GPUs](https://www.youtube.com/watch?v=o0gkdZBtwEg) (видео)
- [The KV Cache: Memory Usage in Transformers](https://www.youtube.com/watch?v=80bIUggRJf4) (видео)

### Смесь экспертов (Mixture of Experts, MoE)
Источник: [узел "Mixture of Experts (MoE)" на roadmap.sh](https://roadmap.sh/inference-engineering/mixture-of-experts-moe@7BddTfOkWmlL4HAkFBXtq)

Модели со смесью экспертов заменяют плотные линейные слои набором меньших матриц-экспертов и активируют для каждого токена только часть экспертов через обученный маршрутизатор. Модель вроде Qwen3-235B активирует за один прямой проход лишь 22 миллиарда из своих 235 миллиардов параметров, поэтому инференс для одного пользователя получается эффективным. При батчевом продакшен-сервинге разные токены активируют разных экспертов, и по батчу в целом задействованы почти все параметры.

Ресурсы:
- [Mixture of Experts Explained](https://huggingface.co/blog/moe) (статья)
- [Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer](https://arxiv.org/abs/1701.06538) (статья)
- [What is Mixture of Experts?](https://www.youtube.com/watch?v=sYDlVVyJYn4) (видео)
- [A Visual Guide to Mixture of Experts (MoE) in LLMs](https://www.youtube.com/watch?v=sOPDGQjFcuM) (видео)

## Модели изображений и видео (Image & Video Models)
Источник: [узел "Image & Video Models" на roadmap.sh](https://roadmap.sh/inference-engineering/image-video-models@Mebx7HS-I-eNP5i3f6Clf)

Модели изображений и видео устроены как специализированные архитектуры ИИ для обработки, интерпретации и генерации визуальных данных. Они используют такие техники, как свёрточные нейронные сети (CNN), трансформеры и диффузионные процессы, чтобы анализировать пиксельные паттерны для задач вроде детекции объектов, классификации изображений и синтеза видеокадров.

Ресурсы:
- [Understanding AI Image Generation: Models, Tools, and Techniques](https://www.digitalocean.com/community/tutorials/understanding-ai-image-generation-models-tools-and-techniques) (статья)
- [How do AI models generate videos?](https://www.technologyreview.com/2025/09/12/1123562/how-do-ai-models-generate-videos/) (статья)
- [What Are Vision Language Models? How AI Sees & Understands Images](https://www.youtube.com/watch?v=lOD_EE96jhM) (видео)
- [But how do AI images and videos actually work?](https://www.youtube.com/watch?v=iv-5mZ_9CPY) (видео)

### Диффузионные модели (Diffusion Models)
Источник: [узел "Diffusion Models" на roadmap.sh](https://roadmap.sh/inference-engineering/diffusion-models@aagMwPPmi6ngfkIqZL-Mg)

Диффузионные модели генерируют изображения, начиная со случайного шума и итеративно убирая его за 30-50 шагов под управлением текстового промпта. На каждом шаге денойзер запускается дважды: один раз с условием (conditioning) и один раз без него, чтобы применить classifier-free guidance. Весь процесс идёт в низкоразмерном латентном пространстве, а не в полном пиксельном, иначе вычисление внимания было бы неподъёмным.

Ресурсы:
- [What are diffusion models?](https://www.ibm.com/think/topics/diffusion-models) (статья)
- [Diffusion Models for AI Image Generation](https://www.youtube.com/watch?v=x2GRE-RzmD8) (видео)
- [How AI Image Generators Work (Stable Diffusion / DALL-E)](https://www.youtube.com/watch?v=1CIpzeNxIhU) (видео)

### Архитектура генерации изображений (Image Generation Architecture)
Источник: [узел "Image Generation Arch." на roadmap.sh](https://roadmap.sh/inference-engineering/image-generation-arch@xsV4WevPzhfydyvxVzGcw)

Модели генерации изображений устроены как пайплайны из нескольких компонентов: текстовый энкодер превращает промпт в условие (conditioning), модель денойзинга итеративно превращает латентное представление из шума в изображение, а вариационный автоэнкодер переводит финальный латент в пиксели. Модель денойзинга, самый крупный и самый затратный по вычислениям компонент, выполняет до 100 прямых проходов за одну генерацию изображения.

Ресурсы:
- [Image Generation Guide](https://ai-guide.future.mozilla.org/content/image-models/) (статья)
- [How AI Image Generators Work (Stable Diffusion / Dall-E)](https://www.youtube.com/watch?v=1CIpzeNxIhU) (видео)

### Генерация изображений за несколько шагов (Few-Step Image Generation)
Источник: [узел "Few-Step Image Generation" на roadmap.sh](https://roadmap.sh/inference-engineering/few-step-image-generation@biVjpCA3bsKI7sa_aBIUE)

Модели генерации изображений за несколько шагов выдают пригодное изображение за восемь или меньше шагов денойзинга: модель обучают сжимать стандартный процесс из 30-50 шагов в малую долю итераций. Среди техник: дистилляция латентной консистентности (latent consistency distillation) и состязательное обучение (adversarial training); обе учат модель доходить до качественного результата за меньшее число проходов. Такие модели хорошо подходят для чувствительных к задержке сценариев вроде фильтров в реальном времени, но дают заметно более низкое качество, чем полношаговые модели. Это решение о выборе модели, а не техника оптимизации инференса.

Ресурсы:
- [Latent Consistency Models: Synthesizing High-Resolution Images with Few-Step Inference](https://arxiv.org/abs/2310.04378) (статья)
- [Few-Step Diffusion Models](https://www.emergentmind.com/topics/few-step-diffusion-model) (статья)

### Модели генерации видео (Video Generation Models)
Источник: [узел "Video Generation Models" на roadmap.sh](https://roadmap.sh/inference-engineering/video-generation-models@yTSrQfJsE-Mf4ZU_hJwYT)

Модели генерации видео расширяют генерацию изображений до трёхмерного латентного пространства, которое одновременно представляет ширину, высоту и время. Они выполняют столько же шагов денойзинга, сколько модели изображений, но обрабатывают гораздо больше данных на каждом шаге. Внимание по всему латентному пространству видео занимает основную часть времени вычислений, поэтому генерация видео оказывается самой ресурсоёмкой из распространённых задач инференса.

Ресурсы:
- [Video Diffusion Models](https://arxiv.org/abs/2204.03458) (статья)
- [How do AI models generate videos?](https://www.technologyreview.com/2025/09/12/1123562/how-do-ai-models-generate-videos/) (статья)
- [Demystifying Video Generation Models](https://adityang5.medium.com/demystifying-video-generation-models-cfac8dbe1913) (статья)
- [How do AI video generation models work?](https://www.youtube.com/watch?v=Y5zHHoLrvAE) (видео)

## Анализ узких мест (Bottleneck Analysis)
Источник: [узел "Bottleneck Analysis" на roadmap.sh](https://roadmap.sh/inference-engineering/bottleneck-analysis@Gtd4g4MtB9zFfahRpbE2K)

Анализ узких мест определяет, чем ограничена конкретная задача инференса: вычислениями или пропускной способностью памяти. От этого зависит, какие оптимизации реально улучшат производительность. Основной инструмент: отношение ops:byte. Сравнение пиковых FLOPS GPU с его пиковой пропускной способностью памяти даёт точку баланса железа, а сравнение арифметической интенсивности операции модели с этой точкой баланса показывает, ограничена она вычислениями или пропускной способностью памяти. Фаза prefill в LLM и генерация изображений ограничены вычислениями; фаза decode в LLM ограничена пропускной способностью памяти.

Ресурсы:
- [The Next AI Bottleneck Isn’t the Model: It’s the Inference System](https://towardsdatascience.com/the-next-ai-bottleneck-isnt-the-model-its-the-inference-system/) (статья)
- [Performance Analysis and Bottleneck Identification in AI Workflows](https://multicorewareinc.com/performance-analysis-and-bottleneck-identification-in-ai-workflows/) (статья)
- [Distributed AI Inference: Why Placement Is the New Bottleneck](https://www.akamai.com/blog/cloud/distributed-ai-inference-why-placement-new-bottleneck) (статья)
- [Inference Optimization Course](https://www.youtube.com/playlist?list=PLXV1pCewfApE) (видео)

### Отношение ops:byte (Ops:Byte Ratio)
Источник: [узел "Ops:Byte Ratio" на roadmap.sh](https://roadmap.sh/inference-engineering/ops-byte-ratio@uc2enkdtRqA5K7kbgrYJF)

Отношение ops:byte описывает свойство GPU: баланс между пропускной способностью вычислений и пропускной способностью памяти. Его считают делением пиковых FLOPS на пиковую пропускную способность памяти; оно задаёт порог, который на этом устройстве отделяет задачи, ограниченные вычислениями, от задач, ограниченных пропускной способностью памяти. У разных поколений GPU отношение ops:byte сильно различается, поэтому оптимизация, которая хорошо работает на одном поколении, может не дать никакого эффекта на другом.

Ресурсы:
- [A guide to LLM inference and performance](https://www.baseten.co/blog/llm-transformer-inference-guide/) (статья)
- [Understanding Performance](https://docs.nvidia.com/deeplearning/performance/dl-performance-gpu-background/index.html#understand-perf) (статья)

### Арифметическая интенсивность (Arithmetic Intensity)
Источник: [узел "Arithmetic Intensity" на roadmap.sh](https://roadmap.sh/inference-engineering/arithmetic-intensity@bPO6uwod30-ewwbo8i1eU)

Арифметическая интенсивность характеризует алгоритм: это число операций с плавающей точкой на каждый байт, прочитанный из памяти или записанный в неё. У большого матричного умножения арифметическая интенсивность высокая, потому что одни и те же веса за одну загрузку участвуют во многих операциях; у прямого прохода на фазе decode она низкая, потому что каждый вес загружается из VRAM и используется один раз на токен. Сравнение арифметической интенсивности задачи с отношением ops:byte GPU даёт самый быстрый способ понять, что поможет: больше вычислений или больше пропускной способности памяти.

Ресурсы:
- [A guide to LLM inference and performance](https://www.baseten.co/blog/llm-transformer-inference-guide/) (статья)
- [Arithmetic Intensity : Understand Op limits - Memory or Compute](https://medium.com/better-ml/arithmetic-intensity-understand-op-limits-memory-or-compute-342fd15342bb) (статья)
- [Arithmetic Intensity Explained: The Formula and Why It Predicts GPU Speedup](https://ayoob.ai/blog/webgpu-matrix-multiplication-gemm-arithmetic-intensity) (статья)
- [Compute-Bound or Memory-Bound? Arithmetic Intensity Explained](https://www.youtube.com/watch?v=jCUWDXVohTY) (видео)

### Модель roofline (Roofline Model)
Источник: [узел "Roofline Model" на roadmap.sh](https://roadmap.sh/inference-engineering/roofline-model@XF-wMQCqPZiWv1XmryPBP)

Модель roofline даёт визуальный способ рассуждать о пределах производительности железа. По оси x откладывают арифметическую интенсивность, по оси y достижимую производительность; на графике два потолка: наклонный потолок пропускной способности памяти для задач с низкой интенсивностью и горизонтальный потолок вычислений для задач с высокой. Положение задачи относительно этих потолков показывает, ограничена ли она вычислениями или пропускной способностью памяти, а также насколько она далека от теоретического максимума железа. Это и есть запас, который остаётся до того, как оптимизация упрётся в жёсткий предел.

Ресурсы:
- [What is the roofline model?](https://modal.com/gpu-glossary/perf/roofline-model) (статья)
- [Calculating inference bottlenecks](https://learn-inference.com/chapters/models/bottlenecks) (статья)
- [A very short intro to the Roofline model](https://www.youtube.com/watch?v=IrkNZG8MJ64) (видео)

### Узкие места инференса LLM (LLM Inference Bottlenecks)
Источник: [узел "LLM Bottlenecks" на roadmap.sh](https://roadmap.sh/inference-engineering/llm-bottlenecks@QVadKzBfLdegat-4wgOMX)

Фаза prefill в LLM ограничена вычислениями: вся входная последовательность обрабатывается одним большим матричным умножением, и на каждый загруженный байт приходится много операций. Фаза decode в LLM ограничена пропускной способностью памяти: токены генерируются по одному через умножения вектора на матрицу, для каждого токена нужно загрузить из памяти все веса модели, а арифметических операций при этом выполняется относительно немного.

Ресурсы:
- [AI Systems Performance Engineering](https://www.oreilly.com/library/view/ai-systems-performance/9781098170202/) (книга)
- [Common Bottlenecks in LLM Inference at Scale (And How to Fix Them)](https://www.yottalabs.ai/post/common-bottlenecks-in-llm-inference-at-scale-and-how-to-fix-them) (статья)
- [GPU Glossary](https://modal.com/gpu-glossary) (статья)
- [The Hidden Bottlenecks in LLM Inference and How to Fix Them](https://www.digitalocean.com/community/conceptual-articles/bottlenecks-llm-inference-optimization) (статья)

### Узкие места генерации изображений и видео (Image and Video Generation Bottlenecks)
Источник: [узел "Image & Video Bottlenecks" на roadmap.sh](https://roadmap.sh/inference-engineering/image-video-bottlenecks@0lRP9cmoS-_wxQSsIcRQg)

Модели генерации изображений и видео ограничены вычислениями: на каждом шаге денойзинга внимание применяется параллельно ко всему латентному пространству, как на фазе prefill в LLM. Сами модели при этом относительно небольшие, так что пропускная способность памяти не становится ограничивающим фактором. Оптимизации направлены на эффективность FLOPS, а не на сокращение трафика памяти.

Ресурсы:
- [How to Overcome Visual Data Bottlenecks in GenAI Development](https://wirestock.io/gen-ai-resources/how-to-overcome-visual-data-bottlenecks-in-genai-development) (статья)
- [6 Limitations of Current AI Video Generation Technology and Workarounds](https://kling.ai/blog/limitations-of-current-ai-video-generation-technology) (статья)
- [The biggest bottleneck in AI video generation is not the model, but the cost.](https://en.eeworld.com.cn/news/wltx/eic737186.html) (статья)
- [But how do AI images and videos actually work?](https://www.youtube.com/watch?v=iv-5mZ_9CPY&t=315s) (видео)

## Оптимизация внимания (Attention Optimization)
Источник: [узел "Attention Optimization" на roadmap.sh](https://roadmap.sh/inference-engineering/attention-optimization@KWM3V7_15_Aur0He9j2Va)

Оптимизация внимания объединяет техники, которые повышают вычислительную эффективность и снижают потребление памяти механизмом внимания в трансформерах. Стандартное внимание масштабируется квадратично от длины входной последовательности, поэтому такие оптимизации стремятся уменьшить объём вычислений и накладные расходы на память. За счёт более экономной организации взаимодействия токенов друг с другом эти методы позволяют моделям быстрее обрабатывать более длинные входы и работать на железе с меньшим объёмом памяти.

Ресурсы:
- [Attention Mechanism Innovation: Next-Generation Focus](https://translated.com/resources/attention-mechanism-innovation-next-generation-focus) (статья)
- [Advanced Attention Mechanisms in Transformer LLMs](https://pub.towardsai.net/advanced-attention-mechanisms-in-transformer-llms-44cac04ec356?gi=22c6a00772a8) (статья)
- [​Sequential Attention: Making AI models leaner and faster without sacrificing accuracy](https://research.google/blog/sequential-attention-making-ai-models-leaner-and-faster-without-sacrificing-accuracy/) (статья)

### FlashAttention
Источник: [узел "FlashAttention" на roadmap.sh](https://roadmap.sh/inference-engineering/flashattention@mQcj-H3R789o6nDh8tG9k)

FlashAttention состоит из серии вручную оптимизированных CUDA-ядер, которые вычисляют внимание с меньшим числом чтений и записей в память GPU: весь алгоритм внимания слит в одно ядро. Стандартное внимание сохраняет промежуточные матрицы в память между шагами; FlashAttention избавляется от этих круговых обращений. FlashAttention 3 рассчитан на GPU Hopper, а FlashAttention 4 на GPU Blackwell.

Ресурсы:
- [Dao-AILab/flash-attention](https://github.com/Dao-AILab/flash-attention) (исходный код)
- [FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](https://arxiv.org/abs/2205.14135) (статья)
- [Flash Attention: The Fastest Attention Mechanism?](https://www.youtube.com/watch?v=eJn6zsbrqUM) (видео)
- [FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning](https://www.youtube.com/playlist?list=PLBWdTDczuFNrxnetcH-5CVLRP1u4Ua87m) (видео)

### PagedAttention
Источник: [узел "PagedAttention" на roadmap.sh](https://roadmap.sh/inference-engineering/pagedattention@VcIRY4vSi7JkcV6g13vkN)

PagedAttention хранит KV-кеш в страницах фиксированного размера, а не в одном непрерывном блоке памяти, поэтому кеш можно распределять по памяти GPU без фрагментации. Доступ к страницам идёт по требованию через таблицу соответствия; это сокращает потери памяти от избыточного выделения и позволяет большему числу запросов делить память GPU. Именно эта техника управления памятью сделала возможной высокую пропускную способность vLLM.

Ресурсы:
- [Efficient Memory Management for Large Language Model Serving with PagedAttention](https://arxiv.org/abs/2309.06180) (статья)
- [PagedAttention](https://handbook.modular.com/inference-optimization/pagedattention/) (статья)
- [PagedAttention: Behind vLLM's Insane Speed](https://www.youtube.com/watch?v=6uPnLkCiy5g) (видео)

### Варианты внимания (Attention Variants)
Источник: [узел "Attention Variants" на roadmap.sh](https://roadmap.sh/inference-engineering/attention-variants@6oTnNEsX_6Cu6lowEz9vg)

Новые алгоритмы внимания снижают квадратичную по времени сложность стандартного внимания. Внимание со скользящим окном (sliding window attention) ограничивает каждый токен обращением к ближайшим w токенам и превращает O(N²) в O(Nw). Линейное внимание (linear attention) аппроксимирует softmax ядром с линейным временем. Сжатое внимание (compressed attention) периодически сжимает более ранний контекст. Эти варианты жертвуют частью качества ради лучшего масштабирования на длинных последовательностях.

Ресурсы:
- [Longformer: The Long-Document Transformer](https://arxiv.org/abs/2004.05150) (статья)
- [Reformer: The Efficient Transformer](https://arxiv.org/abs/2001.04451) (статья)
- [Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation](https://arxiv.org/abs/2108.12409) (статья)
- [Mamba: Linear-Time Sequence Modeling with Selective State Spaces](https://arxiv.org/abs/2312.00752) (статья)
