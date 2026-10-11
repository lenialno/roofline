#!/usr/bin/env python3
"""VRAM budget for a local model directory. Stdlib only.

Weights: sum of *.safetensors bytes when present, else parameter-count estimate from config.json.
KV per token: 2 * layers * kv_heads * head_dim * bytes (MLA: layers * (kv_lora_rank + qk_rope_head_dim) * bytes).
Knobs (env or task vars): GPU_GB=80 (GiB) TP=1 GPU_MEM_UTIL=0.90 OVERHEAD_GB=3 CTX=<max_model_len> KV_DTYPE=auto|fp8 AVG_TOKENS=<ctx/4>
Exit 2 when the config cannot be read.
"""
import glob
import json
import os
import sys


def env_f(name, default):
    v = os.environ.get(name)
    return float(v) if v not in (None, "") else default


def main():
    path = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else os.environ.get("MODEL", "")
    if not path:
        print("vram: usage: task vram MODEL=/path/to/model GPU_GB=80 TP=1 CTX=32768 KV_DTYPE=fp8", file=sys.stderr)
        return 2
    cfg_path = path if path.endswith(".json") else os.path.join(path, "config.json")
    try:
        cfg = json.load(open(cfg_path))
    except Exception as e:
        print("vram: cannot read %s: %s" % (cfg_path, e), file=sys.stderr)
        return 2
    tc = cfg.get("text_config") or cfg  # VLMs nest the LLM config
    layers = tc.get("num_hidden_layers")
    hidden = tc.get("hidden_size")
    heads = tc.get("num_attention_heads")
    kv_heads = tc.get("num_key_value_heads") or heads
    head_dim = tc.get("head_dim") or (hidden // heads if hidden and heads else None)
    vocab = tc.get("vocab_size", 0)
    inter = tc.get("intermediate_size", 0)
    max_pos = tc.get("max_position_embeddings", 0)
    dtype = str(tc.get("torch_dtype", cfg.get("torch_dtype", "bfloat16")))
    qc = cfg.get("quantization_config") or tc.get("quantization_config") or {}
    if not all((layers, hidden, heads, head_dim)):
        print("vram: config lacks num_hidden_layers/hidden_size/num_attention_heads", file=sys.stderr)
        return 2

    # weight bytes per parameter
    if qc:
        bits = qc.get("bits") or qc.get("weight_bits")
        fmt = str(qc.get("quant_method", qc.get("format", ""))).lower()
        if bits:
            wbytes = bits / 8.0
        elif "fp8" in fmt or "float8" in json.dumps(qc).lower():
            wbytes = 1.0
        elif "nvfp4" in fmt or "fp4" in json.dumps(qc).lower():
            wbytes = 0.5
        else:
            wbytes = 1.0
        wsrc = "quantization_config (%s)" % (qc.get("quant_method") or fmt or "?")
    else:
        wbytes = 2.0 if dtype in ("bfloat16", "float16") else 4.0 if dtype == "float32" else 2.0
        wsrc = "torch_dtype %s" % dtype

    files = glob.glob(os.path.join(os.path.dirname(cfg_path), "*.safetensors"))
    if files:
        weights_b = sum(os.path.getsize(f) for f in files)
        wsrc = "%d safetensors files" % len(files)
        params = None
    else:
        experts = tc.get("num_local_experts") or tc.get("num_experts") or tc.get("n_routed_experts") or 0
        moe_inter = tc.get("moe_intermediate_size") or inter
        attn = layers * (hidden * heads * head_dim + 2 * hidden * kv_heads * head_dim + heads * head_dim * hidden)
        if experts:
            mlp = layers * experts * 3 * hidden * moe_inter
        else:
            mlp = layers * 3 * hidden * inter
        params = attn + mlp + 2 * vocab * hidden
        weights_b = params * wbytes

    kv_dtype = os.environ.get("KV_DTYPE", "auto").lower()
    kv_bytes = 1.0 if kv_dtype == "fp8" else 2.0
    if tc.get("kv_lora_rank"):  # MLA (DeepSeek-style)
        kv_per_tok = layers * (tc["kv_lora_rank"] + tc.get("qk_rope_head_dim", 0)) * kv_bytes
        kv_note = "MLA: kv_lora_rank %s + rope %s" % (tc["kv_lora_rank"], tc.get("qk_rope_head_dim", 0))
    else:
        kv_per_tok = 2 * layers * kv_heads * head_dim * kv_bytes
        kv_note = "%d layers x %d kv_heads x %d head_dim x %d B" % (layers, kv_heads, head_dim, kv_bytes)
    if tc.get("sliding_window") and not tc.get("use_sliding_window", True) is False:
        kv_note += "; sliding_window=%s present, real KV may be smaller" % tc.get("sliding_window")

    gpu_gb = env_f("GPU_GB", 80)
    tp = int(env_f("TP", 1))
    util = env_f("GPU_MEM_UTIL", 0.90)
    overhead = env_f("OVERHEAD_GB", 3)
    ctx = int(env_f("CTX", max_pos or 32768))
    avg_tokens = int(env_f("AVG_TOKENS", max(ctx // 4, 1)))

    GB = 1024 ** 3
    weights_gb = weights_b / GB
    usable = gpu_gb * util * tp
    kv_budget = usable - weights_gb - overhead * tp
    tokens_in_kv = int(kv_budget * GB / kv_per_tok) if kv_budget > 0 else 0

    print("model              %s" % os.path.basename(os.path.abspath(os.path.dirname(cfg_path))))
    print("arch               layers=%d hidden=%d heads=%d kv_heads=%d head_dim=%d vocab=%d max_pos=%d" % (layers, hidden, heads, kv_heads, head_dim, vocab, max_pos))
    if params:
        print("params (est)       %.1f B  (from config.json; put the safetensors files next to it for exact weights)" % (params / 1e9))
    print("weights            %.1f GiB (%s, %.2g B/param)" % (weights_gb, wsrc, wbytes))
    print("kv per token       %.0f KB  (%s)" % (kv_per_tok / 1024, kv_note))
    print("gpu budget         %d x %.0f GiB x util %.2f = %.1f GiB usable; overhead %.0f GiB/gpu" % (tp, gpu_gb, util, usable, overhead))
    if kv_budget <= 0:
        print("RESULT             weights do not fit: need %.1f GiB, have %.1f GiB after overhead. Raise TP, quantize, or use a bigger GPU." % (weights_gb, usable - overhead * tp))
        return 1
    print("kv budget          %.1f GiB = %d tokens in flight" % (kv_budget, tokens_in_kv))
    print("concurrency        %d requests at full ctx %d; ~%d requests at avg %d tokens" % (tokens_in_kv // ctx if ctx else 0, ctx, tokens_in_kv // avg_tokens if avg_tokens else 0, avg_tokens))
    if tokens_in_kv < ctx:
        print("WARN               KV budget below one full-context request; lower CTX (max-model-len), use KV_DTYPE=fp8, or raise TP")
    print("suggest            --max-model-len %d  --gpu-memory-utilization %.2f  --max-num-seqs %d  (vLLM)  |  --context-length %d --mem-fraction-static %.2f (SGLang)" % (ctx, util, max(1, min(256, tokens_in_kv // max(avg_tokens, 1))), ctx, util))
    return 0


if __name__ == "__main__":
    sys.exit(main())
