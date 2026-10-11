# Программное обеспечение (Software)

## CUDA
Источник: [узел "CUDA" на roadmap.sh](https://roadmap.sh/inference-engineering/cuda@DwJJLFLPHGn9zdccTlLY2)

CUDA, проприетарная платформа NVIDIA для программирования GPU, состоит из языка ядер (C++), драйвера для управления оборудованием и runtime API для запуска ядер. От CUDA зависят все движки инференса, фреймворки и библиотеки экосистемы NVIDIA, включая cuBLAS, оптимизированную реализацию стандартных процедур линейной алгебры от NVIDIA и бэкенд по умолчанию для умножения матриц в большинстве конвейеров инференса. Понимание CUDA лежит в основе диагностики проблем с производительностью, которые инструменты и движки не могут решить автоматически.

Ресурсы:
- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/) (официальная документация)
- [cuBLAS Documentation](https://docs.nvidia.com/cuda/cublas/) (официальная документация)
- [An Even Easier Introduction to CUDA (Updated)](https://developer.nvidia.com/blog/even-easier-introduction-cuda/) (официальная документация)
- [CUDA Programming Course - High-Performance Computing with GPUs](https://www.youtube.com/watch?v=86FAWCzIe_4) (видео)

### Выбор и слияние ядер (Kernel Selection and Fusion)
Источник: [узел "Kernel Selection & Fusion" на roadmap.sh](https://roadmap.sh/inference-engineering/kernel-selection-fusion@iKW1wqzd5EfRKvNIRshNN)

CUDA-ядром называют функцию, которая выполняется параллельно на тысячах потоков GPU одновременно. Выбор ядра означает подбор лучшего из существующих ядер для конкретной операции; слияние ядер объединяет последовательные ядра в одно, чтобы убрать лишние чтения и записи в VRAM между операциями. Библиотеки вроде cuBLAS, CUTLASS, CuTe и FlashInfer предоставляют готовые ядра для типовых операций инференса, и большинство движков инференса выбирают ядра автоматически.

Ресурсы:
- [What Is a CUDA Kernel? A Visual Explainer](https://llm-stats.com/blog/research/what-is-a-cuda-kernel) (статья)
- [From Zero to GPU: A Guide to Building and Scaling Production-Ready CUDA Kernels](https://huggingface.co/blog/kernel-builder) (статья)
- [How to profile CUDA kernels in PyTorch](https://www.youtube.com/watch?v=LuhJEEJQgUM) (видео)
- [Master Cuda Programming: Zero to Hero](https://www.youtube.com/playlist?list=PLVVBQldz3m5v1VDhlCyB1DhPfjREsJWmf) (видео)

### Написание собственных ядер на Rust (Writing Custom Kernels)
Источник: [узел "Writing Custom Kernels" на roadmap.sh](https://roadmap.sh/inference-engineering/writing-custom-kernels@1dWPVaSQ4TfVU3Obx3m19)

Адаптация: в оригинале узел описывает C++ и Triton; здесь он переписан под Rust, оригинал по ссылке выше.

Собственные ядра пишут, когда существующие библиотеки не используют возможности GPU полностью для конкретной операции или архитектуры. Production-ядра движков инференса (CUTLASS и CuTe для операций типа GEMM, FlashInfer и FlashAttention для вариантов внимания) по-прежнему написаны на CUDA C++, и из Rust их подключают через FFI. Для собственного кода на Rust есть три пути. cudarc даёт безопасные обёртки над драйвером CUDA, NVRTC, cuBLAS, cuBLASLt, cuDNN и NCCL: ядро на CUDA C компилируется в PTX во время выполнения и запускается из Rust; так устроены ядра candle и движка mistral.rs. CubeCL позволяет написать ядро как функцию Rust с атрибутом `#[cube]`, JIT-компилятор переводит её в PTX, HIP, Metal, SPIR-V или WGSL, доступны tensor cores и автотюнинг с кешем результатов; на CubeCL работает фреймворк Burn, проект в статусе alpha. Rust-CUDA компилирует Rust напрямую в PTX через собственный бэкенд rustc; проект перезапущен в 2025 году и находится на ранней стадии. При любом пути эффективное ядро требует понимания иерархии памяти целевого GPU, занятости SM (SM occupancy) и набора инструкций Tensor Core, а это навыки на стыке программной и аппаратной части.

Ресурсы:
- [coreylowman/cudarc](https://github.com/coreylowman/cudarc) (исходный код)
- [tracel-ai/cubecl](https://github.com/tracel-ai/cubecl) (исходный код)
- [Rust-GPU/Rust-CUDA](https://github.com/Rust-GPU/Rust-CUDA) (исходный код)
- [Rust GPU](https://rust-gpu.github.io/) (сайт проекта)
- [huggingface/candle](https://github.com/huggingface/candle) (исходный код)
- [EricLBuehler/mistral.rs](https://github.com/EricLBuehler/mistral.rs) (исходный код)
- [NVRTC Documentation](https://docs.nvidia.com/cuda/nvrtc/index.html) (официальная документация)
- [CUDA by Example: An Introduction to General-Purpose GPU Programming](https://developer.nvidia.com/cuda-example) (книга)
- [cuBLAS Documentation](https://docs.nvidia.com/cuda/cublas/) (официальная документация)
- [Introduction to CUDA](https://docs.nvidia.com/cuda/cuda-programming-guide/part1.html) (официальная документация)
- [NVIDIA/cutlass](https://github.com/NVIDIA/cutlass) (исходный код)

## Фреймворки и библиотеки (Frameworks and Libraries)
Источник: [узел "Frameworks & Libraries" на roadmap.sh](https://roadmap.sh/inference-engineering/frameworks-libraries@D4uNOZgG0w-nFL3a89pDM)

Фреймворки и библиотеки располагаются выше CUDA и ниже движков инференса: они дают абстракции, с которыми инженеры инференса работают напрямую чаще всего. Эта группа охватывает PyTorch и экосистему Hugging Face, которые поставляют реализации моделей и инструменты, от которых зависит остальной стек.

### PyTorch
Источник: [узел "PyTorch" на roadmap.sh](https://roadmap.sh/inference-engineering/pytorch@AHVfxQRXmRoiTxC1eeMme)

PyTorch стал стандартным Python-фреймворком для построения и запуска нейронных сетей. Он абстрагирует CUDA в API тензорных операций и предоставляет автоматическое дифференцирование для обучения. Для инференса PyTorch поддерживает torch.compile для автоматической оптимизации ядер, и на нём построены все основные движки инференса.

Ресурсы:
- [PyTorch Performance Tuning Guide](https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html) (официальная документация)
- [Learn the Basics](https://docs.pytorch.org/tutorials/beginner/basics/intro.html) (официальная документация)
- [Creating a conda Environment for Pytorch and Cuda](https://www.youtube.com/watch?v=_z6WPasIK8U) (видео)
- [How to profile CUDA kernels in PyTorch](https://www.youtube.com/watch?v=LuhJEEJQgUM) (видео)

### Hugging Face Transformers и Diffusers (Hugging Face Transformers and Diffusers)
Источник: [узел "Transformers & Diffusers" на roadmap.sh](https://roadmap.sh/inference-engineering/transformers-diffusers@H_e3KZ7p7enUCYE5M5Lr7)

Библиотеки transformers и diffusers содержат эталонные реализации популярных архитектур LLM и генерации изображений и видео. Они не рассчитаны на production-сервинг, но необходимы, чтобы разбираться в конфигурациях моделей, скачивать веса и прототипировать инференс. Карточки моделей на Hugging Face используют примеры кода на transformers или diffusers как канонические примеры использования.

Ресурсы:
- [Hugging Face Course](https://www.youtube.com/playlist?list=PLo2EIpI_JMQvWfQndUesu0nPBAtZ9gP1o) (курс)
- [Hugging Face Diffusers](https://huggingface.co/docs/diffusers/index) (официальная документация)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index) (официальная документация)
- [Getting Started With Hugging Face in 15 Minutes](https://www.youtube.com/watch?v=QEaBAZQCtwE) (видео)

## Форматы моделей и рантаймы (Model Formats and Runtimes)
Источник: [узел "Model Formats & Runtimes" на roadmap.sh](https://roadmap.sh/inference-engineering/model-formats-runtimes@lTjWXB8YRwx11e8lxSgNm)

Прежде чем модель сможет обслуживать запросы, её веса нужно сохранить, загрузить и скомпилировать в исполняемую форму. Эта группа охватывает файловые форматы для распространения весов и рантаймы, которые компилируют их в оптимизированные движки инференса под конкретное оборудование.

Ресурсы:
- [Common AI Model Formats](https://huggingface.co/blog/ngxson/common-ai-model-formats) (статья)
- [Model Weights File Formats in Machine Learning](https://learnopencv.com/model-weights-file-formats-in-machine-learning/) (статья)

### Safetensors
Источник: [узел "safetensors" на roadmap.sh](https://roadmap.sh/inference-engineering/safetensors@jkbrf0_JDljWmVq_o9XE-)

Safetensors стал стандартным форматом хранения и распространения весов открытых моделей. Он использует отображение в память (memory mapping) для быстрой загрузки без копирования и не допускает выполнения произвольного кода при десериализации, поэтому безопаснее прежних форматов на основе pickle. Все основные движки инференса загружают safetensors нативно, и большинство открытых моделей на Hugging Face публикуют веса в этом формате.

Ресурсы:
- [Safetensors](https://huggingface.co/docs/safetensors/index) (официальная документация)
- [safetensors](https://github.com/safetensors/safetensors) (исходный код)
- [SafeTensors: Efficient Serialization Format for Deep Learning](https://medium.com/@nishthakukreti.01/safetensors-efficient-serialization-format-for-deep-learning-57364317be43) (статья)
- [Hugging Face SafeTensors LLMs in Ollama](https://www.youtube.com/watch?v=DSLwboFJJK4&t=2s) (видео)

### ONNX Runtime
Источник: [узел "ONNX Runtime" на roadmap.sh](https://roadmap.sh/inference-engineering/onnx-runtime@Vmtbdre3SZzwq3FxOO-Bc)

ONNX Runtime, открытый рантайм инференса, выполняет модели, экспортированные в формат ONNX; этот формат хранит и веса, и граф вычислений ради кроссплатформенной переносимости. Он поддерживает несколько аппаратных бэкендов, включая CUDA, DirectML и CPU. Его широко применяют для эмбеддинг-моделей, моделей компьютерного зрения и конвейеров, которым нужно работать в разных аппаратных окружениях без настройки под конкретный движок.

Ресурсы:
- [ONNX Runtime](https://onnxruntime.ai/) (официальная документация)
- [ONNX Runtime Tutorials](https://onnxruntime.ai/docs/tutorials/) (официальная документация)
- [ONNX - open format for machine learning models​](https://www.youtube.com/watch?v=0t2jOBZSd6s) (видео)

### TensorRT
Источник: [узел "TensorRT" на roadmap.sh](https://roadmap.sh/inference-engineering/tensorrt@M4qjJSEAnsjrmP3A_O8HC)

TensorRT, высокопроизводительный рантайм инференса от NVIDIA, компилирует модели PyTorch или ONNX в оптимизированные движки с помощью слитых ядер, квантования и тюнинга под конкретное оборудование. Это стандартный выбор для моделей генерации изображений и видео и для любых нагрузок, где прежде всего нужна максимальная пропускная способность на оборудовании NVIDIA. Скомпилированные движки кешируются на диск, что убирает накладные расходы на перекомпиляцию при последующих холодных стартах.

Ресурсы:
- [TensorRT Documentation](https://docs.nvidia.com/deeplearning/tensorrt/) (официальная документация)
- [TensorRT](https://github.com/nvidia/tensorrt) (исходный код)
- [Inference Optimization with NVIDIA TensorRT](https://www.youtube.com/watch?v=UnIuMXGylfY&list=PLDvBZlLoGspySJggUWsdB40SyGjIcxaxp) (видео)

## Движки инференса (Inference Engines)
Источник: [узел "Inference Engines" на roadmap.sh](https://roadmap.sh/inference-engineering/inference-engines@01j1KkEB-nIXxP-rENcJ3)

Движки инференса образуют основной слой сервинга: они берут веса модели и обрабатывают запросы в production-масштабе. Они реализуют непрерывный батчинг (continuous batching), управление памятью, параллелизм и техники оптимизации, чтобы инженерам не приходилось писать всё это с нуля. Эта группа охватывает три доминирующих движка для LLM и платформу оркестрации, которая работает поверх них.

Ресурсы:
- [What is an Inference Engine & Why it’s Essential for Scalable AI](https://inference.net/content/inference-engine/) (статья)
- [The AI Engineer's Guide to Inference Engines and Frameworks](https://read.theaimerge.com/p/the-ai-engineers-guide-to-inference) (статья)
- [Why so many inference engines..?](https://www.youtube.com/watch?v=_xM8scs4_x4) (видео)

### vLLM
Источник: [узел "vLLM" на roadmap.sh](https://roadmap.sh/inference-engineering/vllm@wcAtbab81IJdpFh6L-heP)

vLLM, самый распространённый движок инференса LLM, широко поддерживает архитектуры моделей, аппаратные платформы (NVIDIA, AMD, Google TPU) и техники оптимизации, включая префиксное кеширование, квантование, спекулятивное декодирование и параллелизм. Его главное преимущество в простоте внедрения и самой быстрой поддержке свежевыпущенных открытых моделей с нулевого дня. Также он поддерживает мультимодальный инференс через vLLM Omni.

Ресурсы:
- [vLLM Docs](https://docs.vllm.ai/en/latest/getting_started/quickstart/) (официальная документация)
- [vllm-project/vllm](https://github.com/vllm-project/vllm) (исходный код)
- [vLLM Course](https://www.youtube.com/playlist?list=PLUBL8w2KtS3M2if8k6-Om_7_sIV_swKRA) (видео)
- [What is vLLM? Efficient AI Inference for Large Language Models](https://www.youtube.com/watch?v=McLdlg5Gc9s) (видео)

### SGLang
Источник: [узел "SGLang" на roadmap.sh](https://roadmap.sh/inference-engineering/sglang@YtlAf6qloKMmaSr9Bkkl_)

SGLang, движок инференса с высокой пропускной способностью, предлагает гибкий фронтенд-язык для настройки поведения сервера. Он хорошо поддерживает MoE-модели вроде DeepSeek и Qwen и тесно работает с лабораториями, выпускающими модели, чтобы оптимизировать новые архитектурные особенности. SGLang Diffusion расширяет его на модели генерации изображений и видео с абстракциями конвейеров и параллелизмом, специфичным для диффузии.

Ресурсы:
- [sglang Docs](https://docs.sglang.io/docs/get-started/quickstart) (официальная документация)
- [sgl-project/sglang](https://github.com/sgl-project/sglang) (исходный код)
- [SGLang vs vLLM: Which LLM Inference Framework Should You Use?](https://www.youtube.com/watch?v=18AkpuX3vkY) (видео)
- [Open-source inference with vLLM + SGLang](https://www.youtube.com/watch?v=R74kx7GKEbs) (видео)

### TensorRT-LLM
Источник: [узел "TensorRT-LLM" на roadmap.sh](https://roadmap.sh/inference-engineering/tensorrt-llm@n2_zIGkQgyYCMYPypz3vb)

TensorRT-LLM, движок инференса от NVIDIA, сочетает выполнение моделей на базе PyTorch с проприетарными ядрами NVIDIA, недоступными в других движках. Он показывает самую высокую производительность среди трёх основных движков, отлично поддерживает архитектуры Hopper и Blackwell и специфичные для NVIDIA форматы вроде NVFP4. Платить за это приходится более крутой кривой обучения и более узкой поддержкой моделей по сравнению с vLLM или SGLang.

Ресурсы:
- [TensorRT-LLM](https://developer.nvidia.com/tensorrt#inference) (официальная документация)
- [NVIDIA/TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM) (исходный код)
- [TensorRT-LLM is Game Changer](https://www.youtube.com/watch?v=FWhK4O1RXxs) (видео)
- [TensorRT LLM 1.0 Livestream: New Easy-To-Use Pythonic Runtime](https://www.youtube.com/watch?v=sTpQQSbta1k) (видео)

### NVIDIA Dynamo
Источник: [узел "NVIDIA Dynamo" на roadmap.sh](https://roadmap.sh/inference-engineering/nvidia-dynamo@ctdMz6rHa4Cwl1x19V_5k)

Dynamo, открытая распределённая платформа сервинга от NVIDIA, работает поверх движков инференса и оркестрирует крупномасштабные развёртывания. Она добавляет маршрутизацию с учётом KV-кеша, дезагрегированный сервинг с раздельными фазами prefill и decode, многоузловой параллелизм и планировщик на основе SLA, который динамически меняет число воркеров prefill и decode в зависимости от целевых TTFT и TPS.

Ресурсы:
- [NVIDIA Dynamo Documentation](https://docs.nvidia.com/dynamo/latest/index.html) (официальная документация)
- [NVIDIA Dynamo](https://www.nvidia.com/en-us/ai/dynamo/) (официальная документация)
- [Distributed Inference 101: Getting Started with NVIDIA Dynamo](https://www.youtube.com/watch?v=1bRmskFCnqY) (видео)
- [NVIDIA Dynamo in 5 Minutes: What Is It and Why Now?](https://www.youtube.com/watch?v=mXYFcz27eDw) (видео)

## Бенчмаркинг и профилирование (Benchmarking and Profiling)
Источник: [узел "Benchmarking & Profiling" на roadmap.sh](https://roadmap.sh/inference-engineering/benchmarking-profiling@TxK7B_FF38ms3eKPGug2w)

С помощью бенчмаркинга и профилирования инженеры инференса превращают интуицию в доказательства. Бенчмаркинг измеряет пропускную способность и задержку системы под нагрузкой; профилирование приближает картину и показывает, какие конкретные операции съедают время. И то и другое необходимо, чтобы принимать решения об оптимизации уверенно.

Ресурсы:
- [Benchmarking AI Inference Providers: How to Compare Performance Fairly](https://www.gmicloud.ai/en/blog/benchmarking-ai-inference-providers) (статья)
- [Benchmarking AI inference on CPUs: A transparent blueprint for the enterprise](https://next.redhat.com/2026/05/28/benchmarking-ai-inference-on-cpus-a-transparent-blueprint-for-the-enterprise/) (статья)
- [LLM Inference Benchmarking: Fundamental Concepts](https://developer.nvidia.com/blog/llm-benchmarking-fundamental-concepts/) (статья)

### Бенчмаркинг производительности (Performance Benchmarking)
Источник: [узел "Performance Benchmarking" на roadmap.sh](https://roadmap.sh/inference-engineering/performance-benchmarking@XXfjlqd0CYHwBR5-Kdmmi)

Бенчмаркинг измеряет производительность сервиса инференса под реалистичной нагрузкой. Хорошие бенчмарки имитируют реалистичные длины входных и выходных последовательностей, паттерны конкурентности и содержимое запросов, а не синтетические однородные входы. Стандартные инструменты: SGLang Genai-bench, NVIDIA GenAI-Perf и Locust. Всегда фиксируйте базовый уровень до применения оптимизаций и меняйте по одной переменной за раз.

Ресурсы:
- [LLM Inference Benchmarking: Fundamental Concepts](https://developer.nvidia.com/blog/llm-benchmarking-fundamental-concepts/) (статья)
- [AI Inference Performance Benchmarks](https://developer.nvidia.com/deep-learning-performance-training-inference/ai-inference) (статья)

### SGLang Genai-bench
Источник: [узел "SGLang Genai-bench" на roadmap.sh](https://roadmap.sh/inference-engineering/sglang-genai-bench@KHDnY7byKgmaPtC_0uDBM)

SGLang Genai-bench, встроенный в проект SGLang инструмент бенчмаркинга, измеряет пропускную способность и задержку инференса LLM при реалистичных распределениях запросов. Он поддерживает переменные длины входных и выходных последовательностей и паттерны конкурентных запросов, поэтому хорошо подходит для проверки развёртываний SGLang и vLLM перед production.

Ресурсы:
- [GenAI Bench](https://sgl-project.github.io/genai-bench/) (официальная документация)
- [genai-bench](https://github.com/sgl-project/genai-bench) (исходный код)

### NVIDIA GenAI-Perf
Источник: [узел "AIPerf" на roadmap.sh](https://roadmap.sh/inference-engineering/aiperf@zffK61pNUJDwkX7Ukql8y)

GenAI-Perf, инструмент бенчмаркинга инференса от NVIDIA, рассчитан на работу с TensorRT-LLM, Triton Inference Server и OpenAI-совместимыми эндпоинтами. Он генерирует синтетические нагрузки с настраиваемыми распределениями длин последовательностей и уровнями конкурентности и выводит стандартные метрики задержки и пропускной способности, включая перцентили TTFT, ITL и TPS.

### Locust
Источник: [узел "Locust" на roadmap.sh](https://roadmap.sh/inference-engineering/locust@IQuJFfMP1dW0ELlip6LOd)

Locust, универсальный открытый фреймворк нагрузочного тестирования на Python, в бенчмаркинге инференса имитирует реалистичные паттерны пользовательского трафика (частоту поступления запросов, плавный рост конкурентности и всплески), которые синтетические инструменты не воспроизводят. Он особенно полезен для сквозного нагрузочного тестирования, которое учитывает сетевые накладные расходы, очереди и поведение автомасштабирования, а не только чистую производительность сервера моделей.

Ресурсы:
- [Locust](https://locust.cloud/) (официальная документация)
- [locust](https://github.com/locustio/locust) (исходный код)
- [LLM Locust: A Tool for Benchmarking LLM Performance](https://www.truefoundry.com/blog/llm-locust-a-tool-for-benchmarking-llm-performance) (статья)

### Профилирование производительности (Profiling Performance)
Источник: [узел "Profiling Performance" на roadmap.sh](https://roadmap.sh/inference-engineering/profiling-performance@S2GZw9etrrvEJzV9V-1C_)

Профилирование показывает, на что уходит время внутри бенчмарка: какие операции потребляют больше всего вычислений или памяти. Инструменты: PyTorch Profiler, NVIDIA Nsight Systems для общесистемного анализа GPU и CPU и NVIDIA Nsight Compute для анализа отдельных ядер. Профилирование полезнее всего при написании собственного кода инференса или вкладе в фреймворки инференса, а не при настройке готовых движков.

Ресурсы:
- [PyTorch Profiler](https://pytorch.org/tutorials/recipes/recipes/profiler_recipe.html) (официальная документация)
- [NVIDIA Nsight Systems](https://developer.nvidia.com/nsight-systems) (официальная документация)
