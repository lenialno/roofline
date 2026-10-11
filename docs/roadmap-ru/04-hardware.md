# Оборудование (Hardware)

## Архитектура GPU (GPU Architecture)
Источник: [узел "GPU Architecture" на roadmap.sh](https://roadmap.sh/inference-engineering/gpu-architecture@00JLMvn8DUJBCw6-BxO0y)

Архитектура GPU задаёт жёсткие пределы того, чего инференс может достичь на конкретном устройстве. Эта группа охватывает вычисления, память, интерконнекты и расчёт ресурсов: четыре измерения, которые инженер инференса должен понимать, чтобы осознанно выбирать железо, стратегию параллелизма и приоритеты оптимизации.

Ресурсы:
- [Programming Massively Parallel Processors](https://www.goodreads.com/work/editions/10244675) (книга)
- [Intro to GPUs](https://max.modular.com/gpu/architecture/) (статья)
- [GPU Glossary](https://modal.com/gpu-glossary) (статья)
- [How do Graphics Cards Work? Exploring GPU Architecture](https://www.youtube.com/watch?v=h9Z4oGN89MU) (видео)

### Вычисления (Compute)
Источник: [узел "Compute" на roadmap.sh](https://roadmap.sh/inference-engineering/compute@o_tknzA4tqcpbU6t5HO-T)

Вычислительные возможности GPU определяются его Streaming Multiprocessors (SM): каждый содержит CUDA Cores для общей арифметики и Tensor Cores для операций умножения-накопления матриц. Главный ресурс инференса, Tensor Cores, выполняет матричные умножения, из которых состоит большая часть вычислений прямого прохода. Вычислительную мощность GPU измеряют в пиковых FLOPS Tensor Cores при заданной точности, и с каждым новым поколением архитектуры NVIDIA она примерно удваивается.

Ресурсы:
- [Understanding GPU Architecture: Structure, Layers, and Performance Explained](https://www.scalecomputing.com/resources/understanding-gpu-architecture) (статья)
- [What Is GPU Computing and How Does It Work? A Complete Guide](https://factory.fpt.ai/ai-insights/what-is-gpu-computing) (статья)
- [Understanding NVIDIA GPU Hardware as a CUDA C Programmer](https://www.youtube.com/watch?v=1Goq8Yc3dfo) (видео)
- [Fundamentals of GPU Architecture](https://www.youtube.com/playlist?list=PLxNPSjHT5qvscDTMaIAY9boOOXAJAS7y4) (видео)

### Память (Memory)
Источник: [узел "Memory" на roadmap.sh](https://roadmap.sh/inference-engineering/memory@5829d5dvXq9qlMSD1CG0N)

Память GPU определяет, что помещается на одно устройство и как быстро данные проходят через вычислительные блоки. Объём VRAM задаёт верхний предел размера модели и KV-кеша; пропускная способность VRAM определяет, как быстро фаза decode может загружать веса на каждый токен. Современные датацентровые GPU используют память с высокой пропускной способностью (HBM) поколений HBM3, HBM3e и HBM4, размещённую стопкой прямо на кристалле GPU ради максимальной пропускной способности.

Ресурсы:
- [What is GPU Memory and Why it Matters for LLM Inference](https://www.bentoml.com/blog/what-is-gpu-memory-and-why-it-matters-for-llm-inference) (статья)
- [What is GPU Memory (VRAM)?](https://www.ertas.ai/glossary/gpu-memory) (статья)
- [NPU vs. CPU vs. GPU vs. TPU: AI Hardware Compared](https://www.youtube.com/watch?v=d3SqH0UBLEY&t=58s) (видео)
- [Memory Hierarchy | GPU Programming](https://www.youtube.com/watch?v=Zrbw0zajhJM) (видео)

### Инстансы и интерконнекты (Instances and Interconnects)
Источник: [узел "Instances & Interconnects" на roadmap.sh](https://roadmap.sh/inference-engineering/instances-interconnects@dAo4PMB_VnRFMSjyDrLj0)

Внутри узла NVLink соединяет GPU напрямую друг с другом на скорости до 1800 ГБ/с на Blackwell, а NVSwitch создаёт фабрику "все со всеми" между всеми восемью GPU. Между узлами связь обеспечивает InfiniBand, с существенно меньшей пропускной способностью, чем у NVLink. Multi-Instance GPU (MIG) делит один GPU на до семи изолированных частей, у каждой свои вычислительные ресурсы и память; так небольшие модели могут работать на долях топового GPU без конкуренции за ресурсы.

Ресурсы:
- [NVLink and NVSwitch](https://www.nvidia.com/en-us/data-center/nvlink/) (официальная документация)
- [NVIDIA InfiniBand](https://www.nvidia.com/en-us/networking/products/infiniband/) (официальная документация)
- [Instances](https://www.baseten.co/inference-engineering/book/03-hardware/instances/) (статья)
- [GPUs: Explained](https://www.youtube.com/watch?v=LfdK-v0SbGI) (видео)

### Расчёт ресурсов и закупка (Sizing and Procurement)
Источник: [узел "Sizing & Procurement" на roadmap.sh](https://roadmap.sh/inference-engineering/sizing-procurement@da0HGfSDr6_DV4ZJcrcIB)

Оценка потребности в GPU начинается с VRAM: примерно 1 ГБ на миллиард параметров в FP8 для весов плюс не меньше 50 процентов запаса под KV-кеш. Итог округляют вверх до ближайшего доступного размера инстанса. Облачные GPU доступны у гиперскейлеров вроде AWS и GCP, у неооблаков (neoclouds) вроде CoreWeave и Nebius, а также на спотовых рынках; крупные развёртывания сочетают зарезервированные инстансы для базовой нагрузки с on-demand и спотовыми мощностями для пиков.

Ресурсы:
- [Designing Data-Intensive Applications](https://dataintensive.net/) (книга)
- [Site Reliability Engineering](https://sre.google/books/) (книга)
- [SemiAnalysis](https://semianalysis.com/) (статья)
- [GPU Requirements for LLM Inference: Memory, Throughput, and Sizing](https://www.onesourcecloud.net/cms/gpu-requirements-llm-inference-sizing.html) (статья)
- [Inference Is the New Bottleneck: How to Plan GPU Capacity for Production AI](https://clear.ml/blog/inference-is-the-new-bottleneck-how-to-plan-gpu-capacity-for-production-ai) (статья)

## Модели GPU (GPU Models)
Источник: [узел "GPU Models" на roadmap.sh](https://roadmap.sh/inference-engineering/gpu-models@umz3jScWQViO9-lACUU4f)

Знание ландшафта GPU (какие устройства доступны, что они дают и как соотносятся друг с другом) нужно на практике для решений о закупке, планирования мощностей и понимания того, какие оптимизации применимы к какому железу. Эта группа охватывает архитектуры NVIDIA, которые доминируют в развёртываниях инференса, и альтернативы, о которых стоит знать.

Ресурсы:
- [12 best GPUs for AI and machine learning in 2026](https://northflank.com/blog/best-gpu-for-ai) (статья)
- [GPU machine types](https://docs.cloud.google.com/compute/docs/gpus) (статья)
- [Every 2026 GPU Brand Explained: What’s the Real Difference?](https://www.youtube.com/watch?v=namWLTrbA1A) (видео)

### NVIDIA
Источник: [узел "NVIDIA" на roadmap.sh](https://roadmap.sh/inference-engineering/nvidia@Uq3mE-0WIASHfcBDEnbLj)

GPU NVIDIA доминируют в инференсе благодаря сочетанию вычислений на Tensor Cores, пропускной способности HBM, интерконнектов NVLink и программной экосистемы CUDA. Для текущих развёртываний инференса важнее всего три архитектуры: Hopper, Blackwell и CPU-платформы Grace и Vera, которые работают с ними в паре.

Ресурсы:
- [Top 12 NVIDIA GPUs for AI Training & Inference in 2026](https://www.atlantic.net/gpu-server-hosting/top-nvidia-gpus-for-ai-training-and-inference/) (статья)
- [Every Nvidia Graphics Card Explained as Simply as Possible](https://www.youtube.com/watch?v=UwPezhj2zoY) (видео)

### Hopper
Источник: [узел "Hopper" на roadmap.sh](https://roadmap.sh/inference-engineering/hopper@XQMbaW1tFdO8Os6mxcR2M)

Архитектура Hopper, выпущенная в 2022 году с H100, а позже с H200, принесла FP8 Tensor Cores с вдвое большей вычислительной пропускной способностью, чем у FP16, и функции асинхронной передачи данных, которые использует FlashAttention 3. GPU H100 и H200 остаются одними из самых распространённых ускорителей инференса благодаря зрелости, широкой поддержке в софте и относительной доступности по сравнению с более новыми поколениями.

Ресурсы:
- [NVIDIA H100 Tensor Core GPU Architecture](https://resources.nvidia.com/en-us-hopper-architecture/nvidia-h100-tensor-c) (официальная документация)
- [NVIDIA Hopper Architecture](https://www.nvidia.com/en-us/data-center/technologies/hopper-architecture/) (официальная документация)
- [What is a Hopper GPU?](https://www.ionos.com/digitalguide/server/know-how/hopper-gpu/) (статья)
- [Nvidia Hopper Explained: Why a 2022 GPU Is Still the Smart Money in 2026](https://www.moduledge.com/blog/nvidia-hopper) (статья)

### Blackwell
Источник: [узел "Blackwell" на roadmap.sh](https://roadmap.sh/inference-engineering/blackwell@LihLABERuKBw30G_j48Fj)

Архитектура Blackwell, выпущенная в конце 2024 года с B200 и B300, добавила FP4 Tensor Cores и новые числовые форматы с микромасштабированием (microscaling), включая MXFP8, MXFP4 и NVFP4. GPU B200 дают примерно 5 PFLOPS вычислений в FP8 и до 8 ТБ/с пропускной способности памяти. Сейчас это золотой стандарт для требовательных задач инференса, включая большие LLM и генерацию видео.

Ресурсы:
- [NVIDIA Blackwell Architecture Technical Brief](https://resources.nvidia.com/en-us-blackwell-architecture) (официальная документация)
- [NVIDIA Blackwell Architecture](https://www.nvidia.com/en-us/data-center/technologies/blackwell-architecture/) (официальная документация)
- [NVIDIA Blackwell GPUs: Architecture, Features, Specs](https://www.nexgencloud.com/blog/performance-benchmarks/nvidia-blackwell-gpus-architecture-features-specs) (статья)

### CPU Grace и Vera (Grace and Vera CPUs)
Источник: [узел "Grace & Vera" на roadmap.sh](https://roadmap.sh/inference-engineering/grace-vera@kPT86kA0WwE_fWUAAKCTT)

ARM-процессоры NVIDIA Grace и Vera соединяются с парными GPU через NVLink Chip-to-Chip на скорости до 900 ГБ/с, что намного выше обычных подключений по PCIe. Такая быстрая связь CPU и GPU делает практичной выгрузку KV-кешей и весов LoRA в память CPU: данные возвращаются достаточно быстро, чтобы оставаться на критическом пути. Grace работает в паре с Hopper и Blackwell, а Vera с готовящейся архитектурой Rubin.

Ресурсы:
- [NVIDIA Grace CPU](https://www.nvidia.com/en-us/data-center/grace-cpu/) (официальная документация)
- [NVIDIA Vera CPU](https://www.nvidia.com/en-us/data-center/vera-cpu/) (официальная документация)
- [NVIDIA Vera/Rubin](https://cb4uhost.com/gpus/vera-rubin) (статья)
- [NVIDIA Vera Rubin: What is it, what's new, and when you can get it](https://www.civo.com/blog/nvidia-vera-rubin) (статья)

### Другие ускорители (Other Accelerators)
Источник: [узел "Other Accelerators" на roadmap.sh](https://roadmap.sh/inference-engineering/other-accelerators@am4Hh-14g6Awk0WcFmVN7)

Альтернативы GPU NVIDIA: AMD MI350, Google TPU, AWS Inferentia и Trainium, Cerebras WSE-3 и Groq LPU. У каждой своё преимущество: AMD даёт CUDA-совместимые инструменты через ROCm; TPU глубоко интегрированы с Google Cloud и JAX; Inferentia и Trainium выигрывают по стоимости внутри AWS. Всем им приходится решать общую задачу: построить экосистему, сопоставимую по широте с библиотеками CUDA от NVIDIA и поддержкой в движках инференса.

Ресурсы:
- [On-Device AI Without NVIDIA](https://www.buildmvpfast.com/blog/on-device-ai-without-nvidia-apple-silicon-intel-alternatives-2026) (статья)
- [Top 12 Cloud GPU Providers for AI and Machine Learning in 2026](https://www.runpod.io/articles/guides/top-cloud-gpu-providers) (статья)
- [Every 2026 GPU Brand Explained: What’s the Real Difference?](https://www.youtube.com/watch?v=namWLTrbA1A) (видео)

## Локальный и edge-инференс (Local and Edge Inference)
Источник: [узел "Local & Edge Inference" на roadmap.sh](https://roadmap.sh/inference-engineering/local-edge-inference@FilQGz3geyyvHZGyKPW3G)

Не весь инференс выполняется в датацентре. У десктопных и мобильных развёртываний другие ограничения по железу, другие экосистемы инструментов и другие сценарии использования, чем у облачного инференса. Эта группа охватывает паттерны и инструменты для запуска моделей на потребительском железе и мобильных устройствах.

Ресурсы:
- [What Is Edge Inference?](https://aws.amazon.com/what-is/edge-inference/) (статья)
- [AI-Focused Edge Inference: Use Cases And Guide for Enterprise](https://www.mirantis.com/blog/ai-focused-edge-inference-use-cases-and-guide-for-enterprise/) (статья)
- [What Is Local Inference? Definition & Requirements](https://ltx.io/glossary/local-inference) (статья)
- [What is Edge AI?](https://www.youtube.com/watch?v=QXuvUW4B7jU&t=232s) (видео)

### Десктопный инференс (Desktop Inference)
Источник: [узел "Desktop Inference" на roadmap.sh](https://roadmap.sh/inference-engineering/desktop-inference@fQDl7_3nRGa8NFivOIgTP)

Десктопный инференс работает на потребительском железе, прежде всего на системах Apple M-серии с unified memory и на топовых потребительских GPU NVIDIA. Железо Apple даёт очень большой объём unified memory при умеренной пропускной способности, поэтому на нём помещаются более крупные модели, чем на дискретных потребительских GPU; потребительские GPU NVIDIA дают более высокую пропускную способность при меньшем объёме. Инструменты вроде Ollama и llama.cpp позволяют запускать агрессивно квантованные модели на потребительском железе с минимальной настройкой.

Ресурсы:
- [Ollama](https://ollama.com/) (официальная документация)
- [LM Studio](https://lmstudio.ai/) (официальная документация)
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) (исходный код)
- [What Is Local AI Inference - and Why It Might Change How You Use AI](https://www.merciaai.com/post/what-is-local-ai-inference-and-why-it-might-change-how-you-use-ai) (статья)

### Мобильный инференс (Mobile Inference)
Источник: [узел "Mobile Inference" на roadmap.sh](https://roadmap.sh/inference-engineering/mobile-inference@kqzHHoiZ9y4tCS6MMlLHQ)

Мобильные устройства выполняют инференс через фреймворки вендоров: Google AI Edge SDK для Android, Apple Foundation Models и Core ML для iOS. Ограничения железа сводят практический размер моделей на современных телефонах к одному-двум миллиардам параметров. Лучше всего для мобильного edge-инференса подходят небольшие дообученные (fine-tuned) модели для задач вроде транскрипции, перевода и классификации на устройстве.

Ресурсы:
- [Shifting AI inference from the cloud to your phone can reduce AI costs](https://www.qualcomm.com/news/onq/2025/09/shifting-ai-inference-from-the-cloud-to-your-phone-can-reduce-ai-costs) (статья)
- [LLM Inference guide for Android](https://developers.google.com/edge/mediapipe/solutions/genai/llm_inference/android) (статья)
- [Cactus: High-Performance AI Inference on Any Smartphone](https://huggingface.co/blog/rshemet/cactus-on-device-inference) (статья)
