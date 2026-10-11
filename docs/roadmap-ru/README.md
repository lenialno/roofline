# Roadmap.sh: Inference Engineering на русском

Перевод всех 136 узлов (27 тем, 109 подтем) карты [roadmap.sh/inference-engineering](https://roadmap.sh/inference-engineering), снимок содержимого от 2026-10-07 через API roadmap.sh. У каждого узла ссылка на оригинал и список ресурсов из карты (названия ссылок оставлены на английском). Порядок файлов повторяет группы карты сверху вниз.

| Файл | Группа | Узлов |
|---|---|---|
| [01-introduction.md](01-introduction.md) | Introduction: открытые и закрытые модели, inference против training, стек инференса | 5 |
| [02-basic-terminology.md](02-basic-terminology.md) | Basic Terminology: метрики задержки, фазы, контекст приложения, стратегия модели | 17 |
| [03-models-and-performance.md](03-models-and-performance.md) | Models & Performance: трансформер, KV-кеш, MoE, диффузия, bottleneck-анализ, attention | 22 |
| [04-hardware.md](04-hardware.md) | Hardware: архитектура GPU, Hopper и Blackwell, локальный инференс | 14 |
| [05-software.md](05-software.md) | Software: CUDA, PyTorch, форматы, vLLM, SGLang, TensorRT-LLM, бенчмарки | 21 |
| [06-inference-techniques.md](06-inference-techniques.md) | Inference Techniques: квантование, спекуляция, кеширование, параллелизм, дезагрегация | 21 |
| [07-inference-beyond-llms.md](07-inference-beyond-llms.md) | Inference Beyond LLMs: VLM, эмбеддинги, речь, генерация изображений и видео | 16 |
| [08-production.md](08-production.md) | Production: контейнеры, автомасштабирование, multi-cloud, выкатка и наблюдаемость | 20 |

Связанные карты по версии roadmap.sh: prompt-engineering, ai-engineer, backend, mlops, devops, docker, kubernetes и cpp; в этом переводе вместо C++ принят [Rust](https://roadmap.sh/rust): узел "Writing Custom Kernels" в [05-software.md](05-software.md) переписан под Rust (cudarc, CubeCL, Rust-CUDA) с пометкой об адаптации, остальные 135 узлов переведены без изменений.

Как это используется в плагине: [карта компетенций](../../skills/roofline-ru/references/competency-map.md) показывает, какие узлы входят в роль on-prem инженера и каким skill или задачей Taskfile закрыты.
