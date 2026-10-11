# Инференс за пределами LLM (Inference Beyond LLMs)

## Визуально-языковые модели (Vision Language Models, VLMs)
Источник: [узел "Vision Language Models" на roadmap.sh](https://roadmap.sh/inference-engineering/vision-language-models@JsjmQrN1V_dM1Kw6UnYLc)

VLM (визуально-языковые модели) объединяют большую языковую модель с небольшим визуальным энкодером, который превращает входные изображения или видео в последовательность визуальных токенов. Изображение высокого разрешения обычно добавляет около 1000 токенов ко входной последовательности. Все техники оптимизации инференса LLM применимы и к VLM, но из-за более длинных последовательностей особенно важны квантование, префиксное кеширование и дезагрегация prefill и decode.

Ресурсы:
- [A Multimodal World - Hugging Face Computer Vision Course](https://huggingface.co/learn/computer-vision-course/en/unit4/multimodal-models/a_multimodal_world) (курс)
- [Vision Language Models Explained](https://huggingface.co/blog/vlms) (статья)
- [What Are Vision Language Models? How AI Sees & Understands Images](https://www.youtube.com/watch?v=lOD_EE96jhM) (видео)
- [Vision Language Models (VLMs)](https://www.youtube.com/playlist?list=PLg9z7TXgYiH3ZOyOENDy72vLMLrmD50Ze) (видео)

### Обработка видео для VLM (Video Processing for VLMs)
Источник: [узел "Video Processing for VLMs" на roadmap.sh](https://roadmap.sh/inference-engineering/video-processing-for-vlms@7pRZu7xa2_43HVwKty9px)

Одна секунда видео содержит 24 кадра, и на каждый при полном разрешении нужно примерно 1000 токенов. Поэтому видео на входе создаёт нагрузку с крайне длинным контекстом. Снижение частоты кадров и даунсемплинг практически обязательны, чтобы прогнать видео через VLM одним запросом. Префиксное кеширование и chunked prefill становятся критичными для работы с получающимися последовательностями из многих тысяч токенов.

Ресурсы:
- [Awesome LLMs for Video Understanding](https://github.com/yunlong10/Awesome-LLMs-for-Video-Understanding) (исходный код)
- [Vision Language Model Prompt Engineering Guide for Image and Video Understanding](https://developer.nvidia.com/blog/vision-language-model-prompt-engineering-guide-for-image-and-video-understanding/) (статья)
- [Exploring the Limits of VLMs: A Dataset for Evaluating Text-to-Video Generation](https://dl.acm.org/doi/full/10.1145/3702250.3702298) (статья)
- [Vision Language Models](https://www.baseten.co/inference-engineering/book/06-modalities/vision-language-models/) (статья)
- [Vision Transformer](https://www.youtube.com/watch?v=vJF3TBI8esQ) (видео)

### Омни-модальные модели (Omni-Modal Models)
Источник: [узел "Omni-Modal Models" на roadmap.sh](https://roadmap.sh/inference-engineering/omni-modal-models@plw2WiOoGxg64P-Kv-Xm7)

Омни-модели принимают несколько входных модальностей и выдают несколько типов выходных данных в одной модели. Они избавляют от задержки последовательного запуска отдельных специализированных моделей, но по качеству внутри каждой модальности часто отстают от выделенных моделей. Продакшен-пайплайны с VLM обычно координируют шаги предобработки, такие как OCR, транскрипция аудио и извлечение текста из PDF, как отдельные независимо масштабируемые компоненты.

Ресурсы:
- [What Is an Omni-Model?](https://www.nvidia.com/en-us/glossary/omni-model/) (статья)
- [Omni-Modal Models](https://www.baseten.co/inference-engineering/book/06-modalities/vision-language-models/#omni-modal-models) (статья)
- [OmniModels: The Unified Architecture for Intelligence](https://medium.com/@frinktyler1445/omnimodels-the-unified-architecture-for-intelligence-89856a63e975) (статья)
- [Qwen3 Omni | Multimodality, Grounding, LLM](https://www.youtube.com/watch?v=tRqEAN61qpk) (видео)

## Эмбеддинг-модели (Embedding Models)
Источник: [узел "Embedding Models" на roadmap.sh](https://roadmap.sh/inference-engineering/embedding-models@Tvt-vX1gWuJZJBHh5vfKu)

Эмбеддинг-модели превращают текст или изображение переменной длины в вектор фиксированной длины, который кодирует семантический смысл. Эти векторы используются в RAG, поиске, рекомендациях и системах памяти агентов. У инференса эмбеддингов два разных профиля трафика: бэкфиллы с высокой пропускной способностью для массовой индексации и выборки с низкой задержкой для пользовательских запросов в реальном времени. Лучше всего обслуживать их отдельными деплоями.

Ресурсы:
- [Hugging Face Embedding Models](https://huggingface.co/models?pipeline_tag=feature-extraction) (официальная документация)
- [BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/abs/1810.04805) (статья)
- [Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks](https://arxiv.org/abs/1908.10084) (статья)
- [Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147) (статья)
- [What Are Embedding Models? Benefits and Best Practices](https://cohere.com/blog/embedding-models) (статья)
- [What is an embedding model?](https://www.youtube.com/watch?v=0U1S0WSsPuE) (видео)

### Модели в стиле BERT (BERT-style Models)
Источник: [узел "BERT-style models" на roadmap.sh](https://roadmap.sh/inference-engineering/bert-style-models@ef3EneMibOaDQkKcpipGY)

Традиционная архитектура для текстовых эмбеддингов это модели в стиле BERT, состоящие только из энкодера: вектор фиксированного размера получается пулингом финальных скрытых состояний двунаправленного трансформера. Они компактные, быстрые и хорошо подходят для индексации с высокой пропускной способностью, когда качества эмбеддингов хватает для задачи. Модели вроде BGE-small и all-MiniLM эффективно работают на CPU или на дробных GPU-инстансах, поэтому это самый дешёвый вариант эмбеддингов.

Ресурсы:
- [SentenceTransformers Documentation](https://sbert.net/) (официальная документация)
- [Using Sentence Transformers at Hugging Face](https://huggingface.co/docs/hub/sentence-transformers) (официальная документация)
- [BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/abs/1810.04805) (статья)
- [Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks](https://arxiv.org/abs/1908.10084) (статья)

### Модели на базе LLM (LLM-based Models)
Источник: [узел "LLM-based models" на roadmap.sh](https://roadmap.sh/inference-engineering/llm-based-models@M7K6d-Qw4BpM724LfM1u6)

Эмбеддинг-модели на базе LLM построены на decoder-only трансформере, обычно от одного до восьми миллиардов параметров, и дают более качественные семантические представления, чем модели в стиле BERT. Они применяют пулинг к скрытым состояниям последнего слоя и обучаются с контрастивными целевыми функциями на крупных поисковых датасетах. Преимущество в качестве сильнее всего заметно на сложных или кросс-языковых задачах поиска. Цена: больше вычислений на один эмбеддинг и инференс на GPU вместо CPU.

Ресурсы:
- [LLM Embeddings Explained: A Visual and Intuitive Guide](https://huggingface.co/spaces/hesamation/primer-llm-embedding?section=what_are_embeddings?) (статья)
- [LLMs are Also Effective Embedding Models: An In-depth Overview](https://arxiv.org/abs/2412.12591) (статья)
- [Understanding Embedding Models in the Context of Large Language Models](https://medium.com/about-ai/understanding-embedding-models-in-the-context-of-large-language-models-02da706ee9b3) (статья)

### Инференс эмбеддинг-моделей (Embedding Model Inference)
Источник: [узел "Embedding Model Inference" на roadmap.sh](https://roadmap.sh/inference-engineering/embedding-model-inference@GmCkfSeVDJ8T8WLZ7DoOp)

TensorRT-LLM с оптимизированным ядром внимания XQA даёт лучшую производительность для эмбеддинг-моделей с LLM-основой. FP8-квантование весов повышает производительность с минимальной потерей качества; проверяют это через косинусное сходство выходных векторов квантованной и исходной моделей. Эмбеддинг-модели достаточно малы, поэтому горизонтальное масштабирование по отдельным GPU-репликам эффективнее, чем параллелизм на нескольких GPU.

Ресурсы:
- [High-performance embedding model inference](https://www.baseten.co/resources/guide/high-performance-embedding-model-inference/#high-performance-embedding-model-inference-how-to-scale-semantic-search-rag-and-agents) (статья)
- [What Actually Makes Embedding Model Inference Fast?](https://filipmakraduli.substack.com/p/what-actually-makes-embedding-model) (статья)
- [Text Embeddings Inference - HuggingFace](https://huggingface.co/docs/text-embeddings-inference/en/index) (статья)

## Речь (Speech)
Источник: [узел "Speech" на roadmap.sh](https://roadmap.sh/inference-engineering/speech@Lk8906Mpi3yxiSt8EC_BC)

Речевой инференс охватывает пайплайн от сырого аудио к тексту и обратно, включая детекцию, транскрипцию, диаризацию и синтез, то есть шаги, из которых складываются голосовые приложения. У каждого компонента свои характеристики инференса, и он часто работает на отдельном железе, чтобы избежать конкуренции за ресурсы.

Ресурсы:
- [TTS Models](https://www.baseten.co/inference-engineering/book/06-modalities/tts-models/) (статья)
- [How streaming ASR inference differs from LLM serving](https://www.youtube.com/watch?v=8HJWwD5Uacc) (видео)
- [Speech LLMs: Models that listen and talk back](https://www.youtube.com/watch?v=MyxgEx4_Moo) (видео)

### Детекция речевой активности (Voice Activity Detection, VAD)
Источник: [узел "Voice Activity Detection" на roadmap.sh](https://roadmap.sh/inference-engineering/voice-activity-detection@P0BA_p3xqpxkQsFHqM0AZ)

VAD это лёгкая модель, которая следит за аудиопотоком или файлом и находит сегменты с речью, отфильтровывая тишину. Это обязательный компонент предобработки и в пайплайнах распознавания речи (ASR) в реальном времени, и в пайплайнах транскрипции длинных файлов: он делит аудио на отдельные чанки по естественным границам речи, а не по фиксированным интервалам времени. VAD работает на выделенном железе, чтобы не конкурировать с ASR-моделью за ресурсы GPU.

Ресурсы:
- [Voice Activity Detection (VAD): The Complete 2026 Guide to Speech Detection](https://picovoice.ai/blog/complete-guide-voice-activity-detection-vad/) (статья)
- [What is voice activity detection (VAD)?](https://soniox.com/wiki/voice-activity-detection) (статья)
- [Voice Activity Detection | The key to realtime voice chat](https://www.youtube.com/watch?v=HUbYXGeR8_c) (видео)

### Распознавание речи (Automatic Speech Recognition, ASR)
Источник: [узел "Auto. Speech Recognition" на roadmap.sh](https://roadmap.sh/inference-engineering/auto-speech-recognition@6PRICRK6aRQCoThxnevB0)

ASR-модели вроде Whisper принимают аудио и выдают текстовую расшифровку. Whisper это encoder-decoder модель, в которой время инференса определяет декодер, авторегрессионный трансформер. Лучшую производительность даёт TensorRT-LLM с in-flight батчингом для декодера. Для транскрипции в реальном времени потоковая передача (стриминг) по WebSocket с чанками, нарезанными VAD, на оптимизированных деплоях укладывается в целевое время полного цикла около 200 миллисекунд на чанк.

Ресурсы:
- [OpenAI Whisper Models on Hugging Face](https://huggingface.co/openai) (официальная документация)
- [What is automatic speech recognition (ASR)?](https://www.ionos.com/digitalguide/websites/web-development/automatic-speech-recognition/) (статья)
- [What is Automatic Speech Recognition? A Comprehensive Overview of ASR Technology](https://www.assemblyai.com/blog/what-is-asr) (статья)
- [How streaming ASR inference differs from LLM serving](https://www.youtube.com/watch?v=8HJWwD5Uacc) (видео)
- [Automatic Speech Recognition - An Overview](https://www.youtube.com/watch?v=q67z7PTGRi8) (видео)

### Синтез речи (Text-to-Speech, TTS)
Источник: [узел "Text-to-Speech (TTS)" на roadmap.sh](https://roadmap.sh/inference-engineering/text-to-speech-tts@XnhhN1QVWzlp9DUwkii9-)

Современные TTS-модели вроде Orpheus TTS это дообученные LLM с расширенным словарём, в который входят аудиотокены. Они генерируют последовательности аудиотокенов, а небольшой аудиодекодер превращает их в волновую форму. Ключевые метрики производительности: время до первого байта аудио (TTFB) и число одновременных потоков в реальном времени, которое выдерживает одна GPU-реплика, а не сырая пропускная способность по токенам.

Ресурсы:
- [What is text to speech?](https://www.ibm.com/think/topics/text-to-speech) (статья)
- [Text-to-Speech](https://huggingface.co/tasks/text-to-speech) (статья)
- [TTS Models](https://www.baseten.co/inference-engineering/book/06-modalities/tts-models/) (статья)
- [Create your own voices with Gemini 3.8 text-to-speech](https://www.youtube.com/watch?v=FL6mI_Br-mc) (видео)

### Потоковый TTS (Streaming TTS)
Источник: [узел "Streaming TTS" на roadmap.sh](https://roadmap.sh/inference-engineering/streaming-tts@3VbPNaSnzWZ-pC-lGFMrh)

TTS в реальном времени непрерывно стримит аудио по WebSocket вместо того, чтобы вернуть готовый файл после окончания генерации. Аудиодекодер превращает потоки токенов в волновую форму по мере их генерации; он реализован на скомпилированном PyTorch с динамическим батчингом. После настройки движка инференса и декодера главный рычаг производительности это число одновременных потоков в реальном времени, которое выдерживает одна GPU-реплика.

Ресурсы:
- [Streaming TTS](https://soniox.com/wiki/streaming-tts) (статья)
- [Streaming Text-to-Speech](https://www.emergentmind.com/topics/streaming-text-to-speech-tts) (статья)
- [Streaming Speech to Text Models - Kyutai vs Whisper](https://www.youtube.com/watch?v=TTx6M4CCbXk) (видео)

### Модели speech-to-speech (Speech-to-Speech Models)
Источник: [узел "Speech-to-Speech Models" на roadmap.sh](https://roadmap.sh/inference-engineering/speech-to-speech-models@moyS740HQoUUovilx1Yyt)

Модели speech-to-speech объединяют ASR, рассуждение и TTS в одной модели: словарь LLM расширяется аудиотокенами на входе и выходе, что убирает задержку каскада из трёх отдельных моделей. Закрытые модели вроде gpt-4o-realtime от OpenAI уже существуют, но пока дороже и слабее хорошо настроенных каскадных пайплайнов из выделенных ASR, LLM и TTS. Открытые speech-to-speech модели остаются активной областью исследований, и на момент написания коммерчески пригодных вариантов нет.

Ресурсы:
- [What Is Speech-to-Speech? Uses, Benefits & How It Works](https://deepgram.com/learn/what-is-speech-to-speech) (статья)
- [Speech-to-Speech LLMs](https://www.emergentmind.com/topics/speech-to-speech-large-language-models-sllms) (статья)
- [Best Speech-to-Speech Model](https://inworld.ai/resources/best-speech-to-speech-model) (статья)
- [Speech-to-Speech Model Research at Google DeepMind](https://www.youtube.com/watch?v=18Um2VjMM_g) (видео)

## Генерация изображений и видео (Image and Video Generation)
Источник: [узел "Image & Video Generation" на roadmap.sh](https://roadmap.sh/inference-engineering/image-video-generation@U0l_xCUiizbJfjfrlBaJ0)

Инференс генерации изображений и видео ограничен вычислениями, а не пропускной способностью памяти, поэтому это другая задача оптимизации, чем сервинг LLM. Группа охватывает продакшен-паттерны, выбор ядер и техники параллелизма, специфичные для деплоя диффузионных моделей.

Ресурсы:
- [Understanding AI Image Generation: Models, Tools, and Techniques](https://www.digitalocean.com/community/tutorials/understanding-ai-image-generation-models-tools-and-techniques) (статья)
- [Understanding AI Video Generation History: Key Concepts and Impact](https://blog.prodia.com/post/understanding-ai-video-generation-history-key-concepts-and-impact) (статья)

### Инференс генерации изображений (Image Generation Inference)
Источник: [узел "Image Generation Inference" на roadmap.sh](https://roadmap.sh/inference-engineering/image-generation-inference@lnIHjq4nvCs3zvUln-jHR)

Продакшен-инференс генерации изображений использует SGLang Diffusion, TensorRT или вручную оптимизированный PyTorch. Самая важная цель оптимизации это ядро внимания: FlashAttention 3 и 4 обгоняют дефолтное ядро на Hopper и Blackwell соответственно. GEMM-ядра линейных слоёв можно безопасно квантовать в FP8. Компиляция через torch с ручными плагинами ядер кеширует скомпилированный движок, чтобы не пересобирать его по несколько минут при каждом холодном старте.

Ресурсы:
- [Image Generation Inference Mechanics](https://github.com/comfyanonymous/ComfyUI) (исходный код)
- [What Is Inference in Generative AI: How It Differs From Traditional Model Inference](https://www.gmicloud.ai/en/blog/what-is-inference-in-generative-ai) (статья)
- [Diffusion Models for AI Image Generation](https://www.youtube.com/watch?v=x2GRE-RzmD8) (видео)
- [Why Does Diffusion Work Better than Auto-Regression?](https://www.youtube.com/watch?v=zc5NTeJbk-k) (видео)

### Инференс генерации видео (Video Generation Inference)
Источник: [узел "Video Generation Inference" на roadmap.sh](https://roadmap.sh/inference-engineering/video-generation-inference@PqEH1ez5dg5tEsspgfAK1)

Модели генерации видео работают на полных нодах из восьми GPU с размером батча один, потому что латентное пространство слишком велико, чтобы его эффективно батчить. Внимание над трёхмерным латентным пространством видео съедает от 70 до 80 процентов времени вычислений и остаётся главной целью оптимизации. Техники кеширования внимания, которые переиспользуют выходы предыдущих временных шагов или слоёв трансформера, ускоряют генерацию на 30 или 40 процентов.

Ресурсы:
- [Cache-DiT](https://github.com/vipshop/cache-dit) (исходный код)
- [TeaCache: Timestep Embedding Tells: It's Time to Cache for Video Diffusion Model](https://github.com/ali-vilab/TeaCache) (исходный код)
- [Video Generation Models](https://www.baseten.co/inference-engineering/book/06-modalities/video-generation-models/) (статья)
- [Video generation - HuggingFace](https://huggingface.co/docs/diffusers/en/using-diffusers/text-img2vid) (статья)
- [How do AI video generation models work?](https://www.youtube.com/watch?v=Y5zHHoLrvAE) (видео)
