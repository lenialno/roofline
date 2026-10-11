# Метрики инференса: определения и формулы

По roadmap.sh (Latency Metrics, Inference Phases) и экспозиции `/metrics` vLLM и SGLang.

| Метрика | Формула | Источник в `/metrics` |
|---|---|---|
| TTFT | t(первый токен) минус t(запрос) | `vllm:time_to_first_token_seconds`, `sglang:time_to_first_token_seconds` |
| TPOT, он же ITL | (t(последний) минус t(первый)) / (N_out минус 1) | `vllm:time_per_output_token_seconds`, `sglang:inter_token_latency_seconds` |
| TPS на поток | 1 / TPOT | расчёт |
| TPS общий | сумма выходных токенов / время окна | `*_generation_tokens_total` по разности за окно |
| e2e | t(конец) минус t(запрос) | `*:e2e_request_latency_seconds` |
| Время в очереди | ожидание до планирования | `vllm:request_queue_time_seconds` |
| Запросы | в работе и в очереди | `vllm:num_requests_running`, `vllm:num_requests_waiting`; `sglang:num_running_reqs`, `sglang:num_queue_reqs` |
| KV usage | доля занятых блоков KV | `vllm:kv_cache_usage_perc`, `sglang:token_usage` |
| Prefix cache hit | hits / queries | `vllm:prefix_cache_hits_total` / `vllm:prefix_cache_queries_total`; `sglang:cache_hit_rate` |
| Preemptions | вытеснения из-за нехватки KV | `vllm:num_preemptions_total` |

Гистограммы в Prometheus кумулятивные с момента старта: `task metrics` считает p50/p95 по бакетам за всё время. Для окна нужен Prometheus с `histogram_quantile(0.95, rate(..._bucket[5m]))`.

## Как связаны

- TTFT = очередь плюс prefill. Prefill compute-bound: время растёт с числом новых (некешированных) токенов промпта
- TPOT определяется чтением весов на каждый шаг: байты весов (после квантования) делить на ширину памяти, плюс чтение KV всех запросов батча
- Увеличение батча делит чтение весов между запросами (общий TPS растёт), но каждый запрос ждёт весь шаг (TPOT растёт)
- Percentiles: распределение скошено вправо длинными промптами; p99 в секунды при хорошей медиане значит, что один из ста пользователей ждёт
- Ops:byte GPU против арифметической интенсивности операции: decode при малом батче далеко ниже порога, поэтому помогает только уменьшение байт (квантование) или рост батча

## Стартовые SLO для кодовых агентов

| Сценарий | TTFT p95 | TPOT p95 | Комментарий |
|---|---|---|---|
| Claude Code, Qwen Code, тёплый кеш | 2 с | 50 мс | промпт 20-60k, большинство токенов из prefix cache |
| холодный промпт 50k | 10 с | 50 мс | чистый prefill; снижать через chunked prefill и больше compute |
| автодополнение | 300 мс | 30 мс | короткие промпты, n-gram спекуляция |
| пакетная обработка | не важен | не важен | только общий TPS и стоимость |

Цифры стартовые; подтверждаются `task bench` на своей модели и GPU.
