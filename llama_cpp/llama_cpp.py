import sys
import os
import ctypes
from ctypes import (
    c_double,
    c_int,
    c_float,
    c_char_p,
    c_int32,
    c_uint32,
    c_void_p,
    c_bool,
    POINTER,
    _Pointer,  # type: ignore
    Structure,
    Array,
    c_uint8,
    c_size_t,
)
import pathlib
from typing import List, Union


# Load the library
def _load_shared_library(lib_base_name: str):
    # Construct the paths to the possible shared library names
    _base_path = pathlib.Path(__file__).parent.resolve()
    # Searching for the library in the current directory under the name "libllama" (default name
    # for llamacpp) and "llama" (default name for this repo)
    _lib_paths: List[pathlib.Path] = []
    # Determine the file extension based on the platform
    if sys.platform.startswith("linux"):
        _lib_paths += [
            _base_path / f"lib{lib_base_name}.so",
        ]
    elif sys.platform == "darwin":
        _lib_paths += [
            _base_path / f"lib{lib_base_name}.so",
            _base_path / f"lib{lib_base_name}.dylib",
        ]
    elif sys.platform == "win32":
        _lib_paths += [
            _base_path / f"{lib_base_name}.dll",
        ]
    else:
        raise RuntimeError("Unsupported platform")

    if "LLAMA_CPP_LIB" in os.environ:
        lib_base_name = os.environ["LLAMA_CPP_LIB"]
        _lib = pathlib.Path(lib_base_name)
        _base_path = _lib.parent.resolve()
        _lib_paths = [_lib.resolve()]

    cdll_args = dict()  # type: ignore
    # Add the library directory to the DLL search path on Windows (if needed)
    if sys.platform == "win32" and sys.version_info >= (3, 8):
        os.add_dll_directory(str(_base_path))
        if "CUDA_PATH" in os.environ:
            os.add_dll_directory(os.path.join(os.environ["CUDA_PATH"], "bin"))
            os.add_dll_directory(os.path.join(os.environ["CUDA_PATH"], "lib"))
        cdll_args["winmode"] = 0

    # Try to load the shared library, handling potential errors
    for _lib_path in _lib_paths:
        if _lib_path.exists():
            try:
                return ctypes.CDLL(str(_lib_path), **cdll_args)
            except Exception as e:
                raise RuntimeError(f"Failed to load shared library '{_lib_path}': {e}")

    raise FileNotFoundError(
        f"Shared library with base name '{lib_base_name}' not found"
    )


# Specify the base name of the shared library to load
_lib_base_name = "llama"

# Load the library
_lib = _load_shared_library(_lib_base_name)

# Misc
c_float_p = POINTER(c_float)
c_uint8_p = POINTER(c_uint8)
c_size_t_p = POINTER(c_size_t)

# llama.h bindings

GGML_USE_CUBLAS = hasattr(_lib, "ggml_init_cublas")
GGML_CUDA_MAX_DEVICES = ctypes.c_int(16)
LLAMA_MAX_DEVICES = GGML_CUDA_MAX_DEVICES if GGML_USE_CUBLAS else ctypes.c_int(1)

# define LLAMA_DEFAULT_SEED 0xFFFFFFFF
LLAMA_DEFAULT_SEED = ctypes.c_int(0xFFFFFFFF)

# define LLAMA_FILE_MAGIC_GGSN 0x6767736eu // 'ggsn'
LLAMA_FILE_MAGIC_GGSN = ctypes.c_uint(0x6767736E)

# define LLAMA_SESSION_MAGIC   LLAMA_FILE_MAGIC_GGSN
LLAMA_SESSION_MAGIC = LLAMA_FILE_MAGIC_GGSN
# define LLAMA_SESSION_VERSION 1
LLAMA_SESSION_VERSION = ctypes.c_int(1)


# struct llama_model;
llama_model_p = c_void_p

# struct llama_context;
llama_context_p = c_void_p


# typedef int llama_token;
llama_token = c_int
llama_token_p = POINTER(llama_token)

# enum llama_log_level {
#     LLAMA_LOG_LEVEL_ERROR = 2,
#     LLAMA_LOG_LEVEL_WARN  = 3,
#     LLAMA_LOG_LEVEL_INFO  = 4
# };
LLAMA_LOG_LEVEL_ERROR = c_int(2)
LLAMA_LOG_LEVEL_WARN = c_int(3)
LLAMA_LOG_LEVEL_INFO = c_int(4)

# enum llama_vocab_type {
#     LLAMA_VOCAB_TYPE_SPM = 0, // SentencePiece
#     LLAMA_VOCAB_TYPE_BPE = 1, // Byte Pair Encoding
# };
LLAMA_VOCAB_TYPE_SPM = c_int(0)
LLAMA_VOCAB_TYPE_BPE = c_int(1)


# enum llama_token_type {
#     LLAMA_TOKEN_TYPE_UNDEFINED    = 0,
#     LLAMA_TOKEN_TYPE_NORMAL       = 1,
#     LLAMA_TOKEN_TYPE_UNKNOWN      = 2,
#     LLAMA_TOKEN_TYPE_CONTROL      = 3,
#     LLAMA_TOKEN_TYPE_USER_DEFINED = 4,
#     LLAMA_TOKEN_TYPE_UNUSED       = 5,
#     LLAMA_TOKEN_TYPE_BYTE         = 6,
# };
LLAMA_TOKEN_TYPE_UNDEFINED = c_int(0)
LLAMA_TOKEN_TYPE_NORMAL = c_int(1)
LLAMA_TOKEN_TYPE_UNKNOWN = c_int(2)
LLAMA_TOKEN_TYPE_CONTROL = c_int(3)
LLAMA_TOKEN_TYPE_USER_DEFINED = c_int(4)
LLAMA_TOKEN_TYPE_UNUSED = c_int(5)
LLAMA_TOKEN_TYPE_BYTE = c_int(6)

# enum llama_ftype {
#     LLAMA_FTYPE_ALL_F32              = 0,
#     LLAMA_FTYPE_MOSTLY_F16           = 1, // except 1d tensors
#     LLAMA_FTYPE_MOSTLY_Q4_0          = 2, // except 1d tensors
#     LLAMA_FTYPE_MOSTLY_Q4_1          = 3, // except 1d tensors
#     LLAMA_FTYPE_MOSTLY_Q4_1_SOME_F16 = 4, // tok_embeddings.weight and output.weight are F16
#     // LLAMA_FTYPE_MOSTLY_Q4_2       = 5, // support has been removed
#     // LLAMA_FTYPE_MOSTLY_Q4_3       = 6, // support has been removed
#     LLAMA_FTYPE_MOSTLY_Q8_0          = 7, // except 1d tensors
#     LLAMA_FTYPE_MOSTLY_Q5_0          = 8, // except 1d tensors
#     LLAMA_FTYPE_MOSTLY_Q5_1          = 9, // except 1d tensors
#     LLAMA_FTYPE_MOSTLY_Q2_K          = 10,// except 1d tensors
#     LLAMA_FTYPE_MOSTLY_Q3_K_S        = 11,// except 1d tensors
#     LLAMA_FTYPE_MOSTLY_Q3_K_M        = 12,// except 1d tensors
#     LLAMA_FTYPE_MOSTLY_Q3_K_L        = 13,// except 1d tensors
#     LLAMA_FTYPE_MOSTLY_Q4_K_S        = 14,// except 1d tensors
#     LLAMA_FTYPE_MOSTLY_Q4_K_M        = 15,// except 1d tensors
#     LLAMA_FTYPE_MOSTLY_Q5_K_S        = 16,// except 1d tensors
#     LLAMA_FTYPE_MOSTLY_Q5_K_M        = 17,// except 1d tensors
#     LLAMA_FTYPE_MOSTLY_Q6_K          = 18,// except 1d tensors
#
#     LLAMA_FTYPE_GUESSED = 1024, // not specified in the model file
# };
LLAMA_FTYPE_ALL_F32 = c_int(0)
LLAMA_FTYPE_MOSTLY_F16 = c_int(1)
LLAMA_FTYPE_MOSTLY_Q4_0 = c_int(2)
LLAMA_FTYPE_MOSTLY_Q4_1 = c_int(3)
LLAMA_FTYPE_MOSTLY_Q4_1_SOME_F16 = c_int(4)
LLAMA_FTYPE_MOSTLY_Q8_0 = c_int(7)
LLAMA_FTYPE_MOSTLY_Q5_0 = c_int(8)
LLAMA_FTYPE_MOSTLY_Q5_1 = c_int(9)
LLAMA_FTYPE_MOSTLY_Q2_K = c_int(10)
LLAMA_FTYPE_MOSTLY_Q3_K_S = c_int(11)
LLAMA_FTYPE_MOSTLY_Q3_K_M = c_int(12)
LLAMA_FTYPE_MOSTLY_Q3_K_L = c_int(13)
LLAMA_FTYPE_MOSTLY_Q4_K_S = c_int(14)
LLAMA_FTYPE_MOSTLY_Q4_K_M = c_int(15)
LLAMA_FTYPE_MOSTLY_Q5_K_S = c_int(16)
LLAMA_FTYPE_MOSTLY_Q5_K_M = c_int(17)
LLAMA_FTYPE_MOSTLY_Q6_K = c_int(18)
LLAMA_FTYPE_GUESSED = c_int(1024)


# typedef struct llama_token_data {
#     llama_token id; // token id
#     float logit;    // log-odds of the token
#     float p;        // probability of the token
# } llama_token_data;
class llama_token_data(Structure):
    _fields_ = [
        ("id", llama_token),
        ("logit", c_float),
        ("p", c_float),
    ]


llama_token_data_p = POINTER(llama_token_data)


# typedef struct llama_token_data_array {
#     llama_token_data * data;
#     size_t size;
#     bool sorted;
# } llama_token_data_array;
class llama_token_data_array(Structure):
    _fields_ = [
        ("data", llama_token_data_p),
        ("size", c_size_t),
        ("sorted", c_bool),
    ]


llama_token_data_array_p = POINTER(llama_token_data_array)

# typedef void (*llama_progress_callback)(float progress, void *ctx);
llama_progress_callback = ctypes.CFUNCTYPE(None, c_float, c_void_p)

# struct llama_context_params {
#     uint32_t seed;         // RNG seed, -1 for random
#     int32_t  n_ctx;        // text context
#     int32_t  n_batch;      // prompt processing batch size
#     int32_t  n_gpu_layers; // number of layers to store in VRAM
#     int32_t  main_gpu;     // the GPU that is used for scratch and small tensors

#     const float * tensor_split; // how to split layers across multiple GPUs (size: LLAMA_MAX_DEVICES)

#     // ref: https://github.com/ggerganov/llama.cpp/pull/2054
#     float    rope_freq_base;  // RoPE base frequency
#     float    rope_freq_scale; // RoPE frequency scaling factor

#     // called with a progress value between 0 and 1, pass NULL to disable
#     llama_progress_callback progress_callback;
#     // context pointer passed to the progress callback
#     void * progress_callback_user_data;


#     // Keep the booleans together to avoid misalignment during copy-by-value.
#     bool low_vram;   // if true, reduce VRAM usage at the cost of performance
#     bool mul_mat_q;  // if true, use experimental mul_mat_q kernels
#     bool f16_kv;     // use fp16 for KV cache
#     bool logits_all; // the llama_eval() call computes all logits, not just the last one
#     bool vocab_only; // only load the vocabulary, no weights
#     bool use_mmap;   // use mmap if possible
#     bool use_mlock;  // force system to keep model in RAM
#     bool embedding;  // embedding mode only
# };
class llama_context_params(Structure):
    _fields_ = [
        ("seed", c_uint32),
        ("n_ctx", c_int32),
        ("n_batch", c_int32),
        ("n_gpu_layers", c_int32),
        ("main_gpu", c_int32),
        ("tensor_split", c_float_p),
        ("rope_freq_base", c_float),
        ("rope_freq_scale", c_float),
        ("progress_callback", llama_progress_callback),
        ("progress_callback_user_data", c_void_p),
        ("low_vram", c_bool),
        ("mul_mat_q", c_bool),
        ("f16_kv", c_bool),
        ("logits_all", c_bool),
        ("vocab_only", c_bool),
        ("use_mmap", c_bool),
        ("use_mlock", c_bool),
        ("embedding", c_bool),
    ]


llama_context_params_p = POINTER(llama_context_params)


# // Signature for logging events
# // Note that text includes the new line character at the end for most events.
# // If your logging mechanism cannot handle that, check if the last character is '\n' and strip it
# // if it exists.
# // It might not exist for progress report where '.' is output repeatedly.
# typedef void (*llama_log_callback)(enum llama_log_level level, const char * text, void * user_data);
llama_log_callback = ctypes.CFUNCTYPE(None, c_int, c_char_p, c_void_p)


# // model quantization parameters
# typedef struct llama_model_quantize_params {
#     int nthread;                 // number of threads to use for quantizing, if <=0 will use std::thread::hardware_concurrency()
#     enum llama_ftype ftype;      // quantize to this llama_ftype
#     bool allow_requantize;       // allow quantizing non-f32/f16 tensors
#     bool quantize_output_tensor; // quantize output.weight
# } llama_model_quantize_params;
class llama_model_quantize_params(Structure):
    _fields_ = [
        ("nthread", c_int),
        ("ftype", c_int),
        ("allow_requantize", c_bool),
        ("quantize_output_tensor", c_bool),
    ]


# // grammar types
# struct llama_grammar;
llama_grammar_p = c_void_p

# // grammar element type
# enum llama_gretype {
#     // end of rule definition
#     LLAMA_GRETYPE_END            = 0,

#     // start of alternate definition for rule
#     LLAMA_GRETYPE_ALT            = 1,

#     // non-terminal element: reference to rule
#     LLAMA_GRETYPE_RULE_REF       = 2,

#     // terminal element: character (code point)
#     LLAMA_GRETYPE_CHAR           = 3,

#     // inverse char(s) ([^a], [^a-b] [^abc])
#     LLAMA_GRETYPE_CHAR_NOT       = 4,

#     // modifies a preceding LLAMA_GRETYPE_CHAR or LLAMA_GRETYPE_CHAR_ALT to
#     // be an inclusive range ([a-z])
#     LLAMA_GRETYPE_CHAR_RNG_UPPER = 5,

#     // modifies a preceding LLAMA_GRETYPE_CHAR or
#     // LLAMA_GRETYPE_CHAR_RNG_UPPER to add an alternate char to match ([ab], [a-zA])
#     LLAMA_GRETYPE_CHAR_ALT       = 6,
# };
LLAMA_GRETYPE_END = c_int(0)
LLAMA_GRETYPE_ALT = c_int(1)
LLAMA_GRETYPE_RULE_REF = c_int(2)
LLAMA_GRETYPE_CHAR = c_int(3)
LLAMA_GRETYPE_CHAR_NOT = c_int(4)
LLAMA_GRETYPE_CHAR_RNG_UPPER = c_int(5)
LLAMA_GRETYPE_CHAR_ALT = c_int(6)


# typedef struct llama_grammar_element {
#     enum llama_gretype type;
#     uint32_t           value; // Unicode code point or rule ID
# } llama_grammar_element;
class llama_grammar_element(Structure):
    _fields_ = [
        ("type", c_int),
        ("value", c_uint32),
    ]


llama_grammar_element_p = POINTER(llama_grammar_element)

# // performance timing information
# struct llama_timings {
#     double t_start_ms;
#     double t_end_ms;
#     double t_load_ms;
#     double t_sample_ms;
#     double t_p_eval_ms;
#     double t_eval_ms;


#     int32_t n_sample;
#     int32_t n_p_eval;
#     int32_t n_eval;
# };
class llama_timings(Structure):
    _fields_ = [
        ("t_start_ms", c_double),
        ("t_end_ms", c_double),
        ("t_load_ms", c_double),
        ("t_sample_ms", c_double),
        ("t_p_eval_ms", c_double),
        ("t_eval_ms", c_double),
        ("n_sample", c_int32),
        ("n_p_eval", c_int32),
        ("n_eval", c_int32),
    ]


# LLAMA_API struct llama_context_params llama_context_default_params(void);
def llama_context_default_params() -> llama_context_params:
    return _lib.llama_context_default_params()


_lib.llama_context_default_params.argtypes = []
_lib.llama_context_default_params.restype = llama_context_params


# LLAMA_API struct llama_model_quantize_params llama_model_quantize_default_params(void);
def llama_model_quantize_default_params() -> llama_model_quantize_params:
    return _lib.llama_model_quantize_default_params()


_lib.llama_model_quantize_default_params.argtypes = []
_lib.llama_model_quantize_default_params.restype = llama_model_quantize_params


# // Initialize the llama + ggml backend
# // If numa is true, use NUMA optimizations
# // Call once at the start of the program
# LLAMA_API void llama_backend_init(bool numa);
def llama_backend_init(numa: c_bool):
    return _lib.llama_backend_init(numa)


_lib.llama_backend_init.argtypes = [c_bool]
_lib.llama_backend_init.restype = None


# // Call once at the end of the program - currently only used for MPI
# LLAMA_API void llama_backend_free(void);
def llama_backend_free():
    return _lib.llama_backend_free()


_lib.llama_backend_free.argtypes = []
_lib.llama_backend_free.restype = None


# LLAMA_API struct llama_model * llama_load_model_from_file(
#                          const char * path_model,
#         struct llama_context_params   params);
def llama_load_model_from_file(
    path_model: bytes, params: llama_context_params
) -> llama_model_p:
    return _lib.llama_load_model_from_file(path_model, params)


_lib.llama_load_model_from_file.argtypes = [c_char_p, llama_context_params]
_lib.llama_load_model_from_file.restype = llama_model_p


# LLAMA_API void llama_free_model(struct llama_model * model);
def llama_free_model(model: llama_model_p):
    return _lib.llama_free_model(model)


_lib.llama_free_model.argtypes = [llama_model_p]
_lib.llama_free_model.restype = None


# LLAMA_API struct llama_context * llama_new_context_with_model(
#                  struct llama_model * model,
#         struct llama_context_params   params);
def llama_new_context_with_model(
    model: llama_model_p, params: llama_context_params
) -> llama_context_p:
    return _lib.llama_new_context_with_model(model, params)


_lib.llama_new_context_with_model.argtypes = [llama_model_p, llama_context_params]
_lib.llama_new_context_with_model.restype = llama_context_p


# // Frees all allocated memory
# LLAMA_API void llama_free(struct llama_context * ctx);
def llama_free(ctx: llama_context_p):
    return _lib.llama_free(ctx)


_lib.llama_free.argtypes = [llama_context_p]
_lib.llama_free.restype = None


# LLAMA_API int64_t llama_time_us(void);
def llama_time_us() -> int:
    return _lib.llama_time_us()


_lib.llama_time_us.argtypes = []
_lib.llama_time_us.restype = ctypes.c_int64


# LLAMA_API int  llama_max_devices    (void);
def llama_max_devices() -> int:
    return _lib.llama_max_devices()


_lib.llama_max_devices.argtypes = []
_lib.llama_max_devices.restype = c_int


# LLAMA_API bool llama_mmap_supported (void);
def llama_mmap_supported() -> bool:
    return _lib.llama_mmap_supported()


_lib.llama_mmap_supported.argtypes = []
_lib.llama_mmap_supported.restype = c_bool


# LLAMA_API bool llama_mlock_supported(void);
def llama_mlock_supported() -> bool:
    return _lib.llama_mlock_supported()


_lib.llama_mlock_supported.argtypes = []
_lib.llama_mlock_supported.restype = c_bool


# LLAMA_API int llama_n_vocab(const struct llama_context * ctx);
def llama_n_vocab(ctx: llama_context_p) -> int:
    return _lib.llama_n_vocab(ctx)


_lib.llama_n_vocab.argtypes = [llama_context_p]
_lib.llama_n_vocab.restype = c_int


# LLAMA_API int llama_n_ctx  (const struct llama_context * ctx);
def llama_n_ctx(ctx: llama_context_p) -> int:
    return _lib.llama_n_ctx(ctx)


_lib.llama_n_ctx.argtypes = [llama_context_p]
_lib.llama_n_ctx.restype = c_int


# LLAMA_API int llama_n_embd (const struct llama_context * ctx);
def llama_n_embd(ctx: llama_context_p) -> int:
    return _lib.llama_n_embd(ctx)


_lib.llama_n_embd.argtypes = [llama_context_p]
_lib.llama_n_embd.restype = c_int


# LLAMA_API enum llama_vocab_type llama_vocab_type(const struct llama_context * ctx);
def llama_vocab_type(ctx: llama_context_p) -> int:
    return _lib.llama_vocab_type(ctx)


_lib.llama_vocab_type.argtypes = [llama_context_p]
_lib.llama_vocab_type.restype = c_int


# LLAMA_API int llama_model_n_vocab(const struct llama_model * model);
def llama_model_n_vocab(model: llama_model_p) -> int:
    return _lib.llama_model_n_vocab(model)


_lib.llama_model_n_vocab.argtypes = [llama_model_p]
_lib.llama_model_n_vocab.restype = c_int


# LLAMA_API int llama_model_n_ctx  (const struct llama_model * model);
def llama_model_n_ctx(model: llama_model_p) -> int:
    return _lib.llama_model_n_ctx(model)


_lib.llama_model_n_ctx.argtypes = [llama_model_p]
_lib.llama_model_n_ctx.restype = c_int


# LLAMA_API int llama_model_n_embd (const struct llama_model * model);
def llama_model_n_embd(model: llama_model_p) -> int:
    return _lib.llama_model_n_embd(model)


_lib.llama_model_n_embd.argtypes = [llama_model_p]
_lib.llama_model_n_embd.restype = c_int


# // Get a string describing the model type
# LLAMA_API int llama_model_desc(const struct llama_model * model, char * buf, size_t buf_size);
def llama_model_desc(model: llama_model_p, buf: bytes, buf_size: c_size_t) -> int:
    return _lib.llama_model_desc(model, buf, buf_size)


_lib.llama_model_desc.argtypes = [llama_model_p, c_char_p, c_size_t]
_lib.llama_model_desc.restype = c_int


# // Returns the total size of all the tensors in the model in bytes
# LLAMA_API uint64_t llama_model_size(const struct llama_model * model);
def llama_model_size(model: llama_model_p) -> int:
    return _lib.llama_model_size(model)


_lib.llama_model_size.argtypes = [llama_model_p]
_lib.llama_model_size.restype = ctypes.c_uint64


# // Returns the total number of parameters in the model
# LLAMA_API uint64_t llama_model_n_params(const struct llama_model * model);
def llama_model_n_params(model: llama_model_p) -> int:
    return _lib.llama_model_n_params(model)


_lib.llama_model_n_params.argtypes = [llama_model_p]
_lib.llama_model_n_params.restype = ctypes.c_uint64


# // Returns 0 on success
# LLAMA_API int llama_model_quantize(
#         const char * fname_inp,
#         const char * fname_out,
#         const llama_model_quantize_params * params);
def llama_model_quantize(
    fname_inp: bytes,
    fname_out: bytes,
    params,  # type: POINTER(llama_model_quantize_params) # type: ignore
) -> int:
    return _lib.llama_model_quantize(fname_inp, fname_out, params)


_lib.llama_model_quantize.argtypes = [
    c_char_p,
    c_char_p,
    POINTER(llama_model_quantize_params),
]
_lib.llama_model_quantize.restype = c_int


# Apply a LoRA adapter to a loaded model
# path_base_model is the path to a higher quality model to use as a base for
# the layers modified by the adapter. Can be NULL to use the current loaded model.
# The model needs to be reloaded before applying a new adapter, otherwise the adapter
# will be applied on top of the previous one
# Returns 0 on success
# LLAMA_API int llama_apply_lora_from_file(
#         struct llama_context * ctx,
#                   const char * path_lora,
#                   const char * path_base_model,
#                          int   n_threads);
def llama_apply_lora_from_file(
    ctx: llama_context_p,
    path_lora: c_char_p,
    path_base_model: c_char_p,
    n_threads: c_int,
) -> int:
    return _lib.llama_apply_lora_from_file(ctx, path_lora, path_base_model, n_threads)


_lib.llama_apply_lora_from_file.argtypes = [llama_context_p, c_char_p, c_char_p, c_int]
_lib.llama_apply_lora_from_file.restype = c_int


# LLAMA_API int llama_model_apply_lora_from_file(
#         const struct llama_model * model,
#                     const char * path_lora,
#                     const char * path_base_model,
#                             int   n_threads);
def llama_model_apply_lora_from_file(
    model: llama_model_p,
    path_lora: Union[c_char_p, bytes],
    path_base_model: Union[c_char_p, bytes],
    n_threads: c_int,
) -> int:
    return _lib.llama_model_apply_lora_from_file(
        model, path_lora, path_base_model, n_threads
    )


_lib.llama_model_apply_lora_from_file.argtypes = [
    llama_model_p,
    c_char_p,
    c_char_p,
    c_int,
]
_lib.llama_model_apply_lora_from_file.restype = c_int


# Returns the number of tokens in the KV cache
# LLAMA_API int llama_get_kv_cache_token_count(const struct llama_context * ctx);
def llama_get_kv_cache_token_count(ctx: llama_context_p) -> int:
    return _lib.llama_get_kv_cache_token_count(ctx)


_lib.llama_get_kv_cache_token_count.argtypes = [llama_context_p]
_lib.llama_get_kv_cache_token_count.restype = c_int


# Sets the current rng seed.
# LLAMA_API void llama_set_rng_seed(struct llama_context * ctx, int seed);
def llama_set_rng_seed(ctx: llama_context_p, seed: c_uint32):
    return _lib.llama_set_rng_seed(ctx, seed)


_lib.llama_set_rng_seed.argtypes = [llama_context_p, c_int]
_lib.llama_set_rng_seed.restype = None


# Returns the maximum size in bytes of the state (rng, logits, embedding
# and kv_cache) - will often be smaller after compacting tokens
# LLAMA_API size_t llama_get_state_size(const struct llama_context * ctx);
def llama_get_state_size(ctx: llama_context_p) -> int:
    return _lib.llama_get_state_size(ctx)


_lib.llama_get_state_size.argtypes = [llama_context_p]
_lib.llama_get_state_size.restype = c_size_t


# Copies the state to the specified destination address.
# Destination needs to have allocated enough memory.
# Returns the number of bytes copied
# LLAMA_API size_t llama_copy_state_data(struct llama_context * ctx, uint8_t * dst);
def llama_copy_state_data(
    ctx: llama_context_p, dst  # type: Array[c_uint8]
) -> int:
    return _lib.llama_copy_state_data(ctx, dst)


_lib.llama_copy_state_data.argtypes = [llama_context_p, c_uint8_p]
_lib.llama_copy_state_data.restype = c_size_t


# Set the state reading from the specified address
# Returns the number of bytes read
# LLAMA_API size_t llama_set_state_data(struct llama_context * ctx, uint8_t * src);
def llama_set_state_data(
    ctx: llama_context_p, src  # type: Array[c_uint8]
) -> int:
    return _lib.llama_set_state_data(ctx, src)


_lib.llama_set_state_data.argtypes = [llama_context_p, c_uint8_p]
_lib.llama_set_state_data.restype = c_size_t


# Save/load session file
# LLAMA_API bool llama_load_session_file(struct llama_context * ctx, const char * path_session, llama_token * tokens_out, size_t n_token_capacity, size_t * n_token_count_out);
def llama_load_session_file(
    ctx: llama_context_p,
    path_session: bytes,
    tokens_out,  # type: Array[llama_token]
    n_token_capacity: c_size_t,
    n_token_count_out,  # type: _Pointer[c_size_t]
) -> int:
    return _lib.llama_load_session_file(
        ctx, path_session, tokens_out, n_token_capacity, n_token_count_out
    )


_lib.llama_load_session_file.argtypes = [
    llama_context_p,
    c_char_p,
    llama_token_p,
    c_size_t,
    c_size_t_p,
]
_lib.llama_load_session_file.restype = c_size_t


# LLAMA_API bool llama_save_session_file(struct llama_context * ctx, const char * path_session, const llama_token * tokens, size_t n_token_count);
def llama_save_session_file(
    ctx: llama_context_p,
    path_session: bytes,
    tokens,  # type: Array[llama_token]
    n_token_count: c_size_t,
) -> int:
    return _lib.llama_save_session_file(ctx, path_session, tokens, n_token_count)


_lib.llama_save_session_file.argtypes = [
    llama_context_p,
    c_char_p,
    llama_token_p,
    c_size_t,
]
_lib.llama_save_session_file.restype = c_size_t


# Run the llama inference to obtain the logits and probabilities for the next token.
# tokens + n_tokens is the provided batch of new tokens to process
# n_past is the number of tokens to use from previous eval calls
# Returns 0 on success
# LLAMA_API int llama_eval(
#         struct llama_context * ctx,
#            const llama_token * tokens,
#                          int   n_tokens,
#                          int   n_past,
#                          int   n_threads);
def llama_eval(
    ctx: llama_context_p,
    tokens,  # type: Array[llama_token]
    n_tokens: c_int,
    n_past: c_int,
    n_threads: c_int,
) -> int:
    return _lib.llama_eval(ctx, tokens, n_tokens, n_past, n_threads)


_lib.llama_eval.argtypes = [llama_context_p, llama_token_p, c_int, c_int, c_int]
_lib.llama_eval.restype = c_int


# // Same as llama_eval, but use float matrix input directly.
# LLAMA_API int llama_eval_embd(
#         struct llama_context * ctx,
#                     const float * embd,
#                             int   n_tokens,
#                             int   n_past,
#                             int   n_threads);
def llama_eval_embd(
    ctx: llama_context_p,
    embd,  # type: Array[c_float]
    n_tokens: c_int,
    n_past: c_int,
    n_threads: c_int,
) -> int:
    return _lib.llama_eval_embd(ctx, embd, n_tokens, n_past, n_threads)


_lib.llama_eval_embd.argtypes = [llama_context_p, c_float_p, c_int, c_int, c_int]
_lib.llama_eval_embd.restype = c_int


# // Export a static computation graph for context of 511 and batch size of 1
# // NOTE: since this functionality is mostly for debugging and demonstration purposes, we hardcode these
# //       parameters here to keep things simple
# // IMPORTANT: do not use for anything else other than debugging and testing!
# LLAMA_API int llama_eval_export(struct llama_context * ctx, const char * fname);
def llama_eval_export(ctx: llama_context_p, fname: bytes) -> int:
    return _lib.llama_eval_export(ctx, fname)


_lib.llama_eval_export.argtypes = [llama_context_p, c_char_p]
_lib.llama_eval_export.restype = c_int


# Token logits obtained from the last call to llama_eval()
# The logits for the last token are stored in the last row
# Can be mutated in order to change the probabilities of the next token
# Rows: n_tokens
# Cols: n_vocab
# LLAMA_API float * llama_get_logits(struct llama_context * ctx);
def llama_get_logits(
    ctx: llama_context_p,
):  # type: (...) -> Array[float] # type: ignore
    return _lib.llama_get_logits(ctx)


_lib.llama_get_logits.argtypes = [llama_context_p]
_lib.llama_get_logits.restype = c_float_p


# Get the embeddings for the input
# shape: [n_embd] (1-dimensional)
# LLAMA_API float * llama_get_embeddings(struct llama_context * ctx);
def llama_get_embeddings(
    ctx: llama_context_p,
):  # type: (...) -> Array[float] # type: ignore
    return _lib.llama_get_embeddings(ctx)


_lib.llama_get_embeddings.argtypes = [llama_context_p]
_lib.llama_get_embeddings.restype = c_float_p


# //
# // Vocab
# //


# LLAMA_API const char * llama_token_get_text(const struct llama_context * ctx, llama_token token);
def llama_token_get_text(ctx: llama_context_p, token: llama_token) -> bytes:
    return _lib.llama_token_get_text(ctx, token)


_lib.llama_token_get_text.argtypes = [llama_context_p, llama_token]
_lib.llama_token_get_text.restype = c_char_p


# LLAMA_API float llama_token_get_score(const struct llama_context * ctx, llama_token token);
def llama_token_get_score(ctx: llama_context_p, token: llama_token) -> float:
    return _lib.llama_token_get_score(ctx, token)


_lib.llama_token_get_score.argtypes = [llama_context_p, llama_token]
_lib.llama_token_get_score.restype = c_float


# LLAMA_API enum llama_token_type llama_token_get_type(const struct llama_context * ctx, llama_token token);
def llama_token_get_type(ctx: llama_context_p, token: llama_token) -> int:
    return _lib.llama_token_get_type(ctx, token)


_lib.llama_token_get_type.argtypes = [llama_context_p, llama_token]
_lib.llama_token_get_type.restype = ctypes.c_int


# // Special tokens


# LLAMA_API llama_token llama_token_bos(const struct llama_context * ctx);  // beginning-of-sentence
def llama_token_bos(ctx: llama_context_p) -> llama_token:
    return _lib.llama_token_bos(ctx)


_lib.llama_token_bos.argtypes = [llama_context_p]
_lib.llama_token_bos.restype = llama_token


# LLAMA_API llama_token llama_token_eos(const struct llama_context * ctx);  // end-of-sentence
def llama_token_eos(ctx: llama_context_p) -> llama_token:
    return _lib.llama_token_eos(ctx)


_lib.llama_token_eos.argtypes = [llama_context_p]
_lib.llama_token_eos.restype = llama_token


# LLAMA_API llama_token llama_token_nl (const struct llama_context * ctx);  // next-line
def llama_token_nl(ctx: llama_context_p) -> llama_token:
    return _lib.llama_token_nl(ctx)


_lib.llama_token_nl.argtypes = [llama_context_p]
_lib.llama_token_nl.restype = llama_token


# //
# // Tokenization
# //


# Convert the provided text into tokens.
# The tokens pointer must be large enough to hold the resulting tokens.
# Returns the number of tokens on success, no more than n_max_tokens
# Returns a negative number on failure - the number of tokens that would have been returned
# TODO: not sure if correct
# LLAMA_API int llama_tokenize(
#         struct llama_context * ctx,
#                   const char * text,
#                  llama_token * tokens,
#                          int   n_max_tokens,
#                         bool   add_bos);
def llama_tokenize(
    ctx: llama_context_p,
    text: bytes,
    tokens,  # type: Array[llama_token]
    n_max_tokens: c_int,
    add_bos: c_bool,
) -> int:
    return _lib.llama_tokenize(ctx, text, tokens, n_max_tokens, add_bos)


_lib.llama_tokenize.argtypes = [llama_context_p, c_char_p, llama_token_p, c_int, c_bool]
_lib.llama_tokenize.restype = c_int


# LLAMA_API int llama_tokenize_with_model(
#     const struct llama_model * model,
#                   const char * text,
#                  llama_token * tokens,
#                          int   n_max_tokens,
#                         bool   add_bos);
def llama_tokenize_with_model(
    model: llama_model_p,
    text: bytes,
    tokens,  # type: Array[llama_token]
    n_max_tokens: c_int,
    add_bos: c_bool,
) -> int:
    return _lib.llama_tokenize_with_model(model, text, tokens, n_max_tokens, add_bos)


_lib.llama_tokenize_with_model.argtypes = [
    llama_model_p,
    c_char_p,
    llama_token_p,
    c_int,
    c_bool,
]
_lib.llama_tokenize_with_model.restype = c_int


# // Token Id -> Piece.
# // Uses the vocabulary in the provided context.
# // Does not write null terminator to the buffer.
# // User code is responsible to remove the leading whitespace of the first non-BOS token when decoding multiple tokens.
# LLAMA_API int llama_token_to_piece(
#         const struct llama_context * ctx,
#                         llama_token   token,
#                                 char * buf,
#                                 int    length);
def llama_token_to_piece(
    ctx: llama_context_p, token: llama_token, buf: bytes, length: c_int
) -> int:
    return _lib.llama_token_to_piece(ctx, token, buf, length)


_lib.llama_token_to_piece.argtypes = [llama_context_p, llama_token, c_char_p, c_int]
_lib.llama_token_to_piece.restype = c_int


# LLAMA_API int llama_token_to_piece_with_model(
#             const struct llama_model * model,
#                         llama_token   token,
#                                 char * buf,
#                                 int    length);
def llama_token_to_piece_with_model(
    model: llama_model_p, token: llama_token, buf: bytes, length: c_int
) -> int:
    return _lib.llama_token_to_piece_with_model(model, token, buf, length)


_lib.llama_token_to_piece_with_model.argtypes = [
    llama_model_p,
    llama_token,
    c_char_p,
    c_int,
]
_lib.llama_token_to_piece_with_model.restype = c_int

# //
# // Grammar
# //


# LLAMA_API struct llama_grammar * llama_grammar_init(
#         const llama_grammar_element ** rules,
#                                 size_t    n_rules,
#                                 size_t    start_rule_index);
def llama_grammar_init(
    rules,  # type: Array[llama_grammar_element_p] # type: ignore
    n_rules: c_size_t,
    start_rule_index: c_size_t,
) -> llama_grammar_p:
    return _lib.llama_grammar_init(rules, n_rules, start_rule_index)


_lib.llama_grammar_init.argtypes = [
    POINTER(llama_grammar_element_p),
    c_size_t,
    c_size_t,
]
_lib.llama_grammar_init.restype = llama_grammar_p


# LLAMA_API void llama_grammar_free(struct llama_grammar * grammar);
def llama_grammar_free(grammar: llama_grammar_p):
    return _lib.llama_grammar_free(grammar)


_lib.llama_grammar_free.argtypes = [llama_grammar_p]
_lib.llama_grammar_free.restype = None

# //
# // Beam search
# //


# struct llama_beam_view {
#     const llama_token * tokens;
#     size_t n_tokens;
#     float p;   // Cumulative beam probability (renormalized relative to all beams)
#     bool eob;  // Callback should set this to true when a beam is at end-of-beam.
# };
class llama_beam_view(ctypes.Structure):
    _fields_ = [
        ("tokens", llama_token_p),
        ("n_tokens", c_size_t),
        ("p", c_float),
        ("eob", c_bool),
    ]


# // Passed to beam_search_callback function.
# // Whenever 0 < common_prefix_length, this number of tokens should be copied from any of the beams
# // (e.g. beams[0]) as they will be removed (shifted) from all beams in all subsequent callbacks.
# // These pointers are valid only during the synchronous callback, so should not be saved.
# struct llama_beams_state {
#     struct llama_beam_view * beam_views;
#     size_t n_beams;               // Number of elements in beam_views[].
#     size_t common_prefix_length;  // Current max length of prefix tokens shared by all beams.
#     bool last_call;               // True iff this is the last callback invocation.
# };
class llama_beams_state(ctypes.Structure):
    _fields_ = [
        ("beam_views", POINTER(llama_beam_view)),
        ("n_beams", c_size_t),
        ("common_prefix_length", c_size_t),
        ("last_call", c_bool),
    ]


# // Type of pointer to the beam_search_callback function.
# // void* callback_data is any custom data passed to llama_beam_search, that is subsequently
# // passed back to beam_search_callback. This avoids having to use global variables in the callback.
# typedef void (*llama_beam_search_callback_fn_t)(void * callback_data, struct llama_beams_state);
llama_beam_search_callback_fn_t = ctypes.CFUNCTYPE(None, c_void_p, llama_beams_state)


# /// @details Deterministically returns entire sentence constructed by a beam search.
# /// @param ctx Pointer to the llama_context.
# /// @param callback Invoked for each iteration of the beam_search loop, passing in beams_state.
# /// @param callback_data A pointer that is simply passed back to callback.
# /// @param n_beams Number of beams to use.
# /// @param n_past Number of tokens already evaluated.
# /// @param n_predict Maximum number of tokens to predict. EOS may occur earlier.
# /// @param n_threads Number of threads as passed to llama_eval().
# LLAMA_API void llama_beam_search(struct llama_context * ctx, llama_beam_search_callback_fn_t callback, void * callback_data, size_t n_beams, int n_past, int n_predict, int n_threads);
def llama_beam_search(
    ctx: llama_context_p,
    callback: "ctypes._CFuncPtr[None, c_void_p, llama_beams_state]",  # type: ignore
    callback_data: c_void_p,
    n_beams: c_size_t,
    n_past: c_int,
    n_predict: c_int,
    n_threads: c_int,
):
    return _lib.llama_beam_search(
        ctx, callback, callback_data, n_beams, n_past, n_predict, n_threads
    )


# //
# // Sampling functions
# //


# @details Repetition penalty described in CTRL academic paper https://arxiv.org/abs/1909.05858, with negative logit fix.
# LLAMA_API void llama_sample_repetition_penalty(struct llama_context * ctx, llama_token_data_array * candidates, const llama_token * last_tokens, size_t last_tokens_size, float penalty);
def llama_sample_repetition_penalty(
    ctx: llama_context_p,
    candidates,  # type: _Pointer[llama_token_data_array]
    last_tokens_data,  # type: Array[llama_token]
    last_tokens_size: c_int,
    penalty: c_float,
):
    return _lib.llama_sample_repetition_penalty(
        ctx, candidates, last_tokens_data, last_tokens_size, penalty
    )


_lib.llama_sample_repetition_penalty.argtypes = [
    llama_context_p,
    llama_token_data_array_p,
    llama_token_p,
    c_int,
    c_float,
]
_lib.llama_sample_repetition_penalty.restype = None


# @details Frequency and presence penalties described in OpenAI API https://platform.openai.com/docs/api-reference/parameter-details.
# LLAMA_API void llama_sample_frequency_and_presence_penalties(struct llama_context * ctx, llama_token_data_array * candidates, const llama_token * last_tokens, size_t last_tokens_size, float alpha_frequency, float alpha_presence);
def llama_sample_frequency_and_presence_penalties(
    ctx: llama_context_p,
    candidates,  # type: _Pointer[llama_token_data_array]
    last_tokens_data,  # type: Array[llama_token]
    last_tokens_size: c_int,
    alpha_frequency: c_float,
    alpha_presence: c_float,
):
    return _lib.llama_sample_frequency_and_presence_penalties(
        ctx,
        candidates,
        last_tokens_data,
        last_tokens_size,
        alpha_frequency,
        alpha_presence,
    )


_lib.llama_sample_frequency_and_presence_penalties.argtypes = [
    llama_context_p,
    llama_token_data_array_p,
    llama_token_p,
    c_int,
    c_float,
    c_float,
]
_lib.llama_sample_frequency_and_presence_penalties.restype = None


# /// @details Apply classifier-free guidance to the logits as described in academic paper "Stay on topic with Classifier-Free Guidance" https://arxiv.org/abs/2306.17806
# /// @param candidates A vector of `llama_token_data` containing the candidate tokens, the logits must be directly extracted from the original generation context without being sorted.
# /// @params guidance_ctx A separate context from the same model. Other than a negative prompt at the beginning, it should have all generated and user input tokens copied from the main context.
# /// @params scale Guidance strength. 1.0f means no guidance. Higher values mean stronger guidance.
# LLAMA_API void llama_sample_classifier_free_guidance(
#             struct llama_context * ctx,
#         llama_token_data_array * candidates,
#             struct llama_context * guidance_ctx,
#                             float   scale);
def llama_sample_classifier_free_guidance(
    ctx: llama_context_p,
    candidates,  # type: _Pointer[llama_token_data_array]
    guidance_ctx: llama_context_p,
    scale: c_float,
):
    return _lib.llama_sample_classifier_free_guidance(
        ctx, candidates, guidance_ctx, scale
    )


_lib.llama_sample_classifier_free_guidance.argtypes = [
    llama_context_p,
    llama_token_data_array_p,
    llama_context_p,
    c_float,
]
_lib.llama_sample_classifier_free_guidance.restype = None


# @details Sorts candidate tokens by their logits in descending order and calculate probabilities based on logits.
# LLAMA_API void llama_sample_softmax(struct llama_context * ctx, llama_token_data_array * candidates);
def llama_sample_softmax(
    ctx: llama_context_p, candidates  # type: _Pointer[llama_token_data]
):
    return _lib.llama_sample_softmax(ctx, candidates)


_lib.llama_sample_softmax.argtypes = [
    llama_context_p,
    llama_token_data_array_p,
]
_lib.llama_sample_softmax.restype = None


# @details Top-K sampling described in academic paper "The Curious Case of Neural Text Degeneration" https://arxiv.org/abs/1904.09751
# LLAMA_API void llama_sample_top_k(struct llama_context * ctx, llama_token_data_array * candidates, int k, size_t min_keep);
def llama_sample_top_k(
    ctx: llama_context_p,
    candidates,  # type: _Pointer[llama_token_data_array]
    k: c_int,
    min_keep: c_size_t,
):
    return _lib.llama_sample_top_k(ctx, candidates, k, min_keep)


_lib.llama_sample_top_k.argtypes = [
    llama_context_p,
    llama_token_data_array_p,
    c_int,
    c_size_t,
]
_lib.llama_sample_top_k.restype = None


# @details Nucleus sampling described in academic paper "The Curious Case of Neural Text Degeneration" https://arxiv.org/abs/1904.09751
# LLAMA_API void llama_sample_top_p(struct llama_context * ctx, llama_token_data_array * candidates, float p, size_t min_keep);
def llama_sample_top_p(
    ctx: llama_context_p,
    candidates,  # type: _Pointer[llama_token_data_array]
    p: c_float,
    min_keep: c_size_t,
):
    return _lib.llama_sample_top_p(ctx, candidates, p, min_keep)


_lib.llama_sample_top_p.argtypes = [
    llama_context_p,
    llama_token_data_array_p,
    c_float,
    c_size_t,
]
_lib.llama_sample_top_p.restype = None


# @details Tail Free Sampling described in https://www.trentonbricken.com/Tail-Free-Sampling/.
# LLAMA_API void llama_sample_tail_free(struct llama_context * ctx, llama_token_data_array * candidates, float z, size_t min_keep);
def llama_sample_tail_free(
    ctx: llama_context_p,
    candidates,  # type: _Pointer[llama_token_data_array]
    z: c_float,
    min_keep: c_size_t,
):
    return _lib.llama_sample_tail_free(ctx, candidates, z, min_keep)


_lib.llama_sample_tail_free.argtypes = [
    llama_context_p,
    llama_token_data_array_p,
    c_float,
    c_size_t,
]
_lib.llama_sample_tail_free.restype = None


# @details Locally Typical Sampling implementation described in the paper https://arxiv.org/abs/2202.00666.
# LLAMA_API void llama_sample_typical(struct llama_context * ctx, llama_token_data_array * candidates, float p, size_t min_keep);
def llama_sample_typical(
    ctx: llama_context_p,
    candidates,  # type: _Pointer[llama_token_data_array]
    p: c_float,
    min_keep: c_size_t,
):
    return _lib.llama_sample_typical(ctx, candidates, p, min_keep)


_lib.llama_sample_typical.argtypes = [
    llama_context_p,
    llama_token_data_array_p,
    c_float,
    c_size_t,
]
_lib.llama_sample_typical.restype = None


# LLAMA_API void llama_sample_temperature(struct llama_context * ctx, llama_token_data_array * candidates, float temp);
def llama_sample_temperature(
    ctx: llama_context_p,
    candidates,  # type: _Pointer[llama_token_data_array]
    temp: c_float,
):
    return _lib.llama_sample_temperature(ctx, candidates, temp)


_lib.llama_sample_temperature.argtypes = [
    llama_context_p,
    llama_token_data_array_p,
    c_float,
]
_lib.llama_sample_temperature.restype = None


# LLAMA_API void llama_sample_grammar(struct llama_context * ctx, llama_token_data_array * candidates, const struct llama_grammar * grammar);
def llama_sample_grammar(
    ctx: llama_context_p,
    candidates,  # type: _Pointer[llama_token_data_array]
    grammar,  # type: llama_grammar_p
):
    return _lib.llama_sample_grammar(ctx, candidates, grammar)


_lib.llama_sample_grammar.argtypes = [
    llama_context_p,
    llama_token_data_array_p,
    llama_grammar_p,
]
_lib.llama_sample_grammar.restype = None


# @details Mirostat 1.0 algorithm described in the paper https://arxiv.org/abs/2007.14966. Uses tokens instead of words.
# @param candidates A vector of `llama_token_data` containing the candidate tokens, their probabilities (p), and log-odds (logit) for the current position in the generated text.
# @param tau  The target cross-entropy (or surprise) value you want to achieve for the generated text. A higher value corresponds to more surprising or less predictable text, while a lower value corresponds to less surprising or more predictable text.
# @param eta The learning rate used to update `mu` based on the error between the target and observed surprisal of the sampled word. A larger learning rate will cause `mu` to be updated more quickly, while a smaller learning rate will result in slower updates.
# @param m The number of tokens considered in the estimation of `s_hat`. This is an arbitrary value that is used to calculate `s_hat`, which in turn helps to calculate the value of `k`. In the paper, they use `m = 100`, but you can experiment with different values to see how it affects the performance of the algorithm.
# @param mu Maximum cross-entropy. This value is initialized to be twice the target cross-entropy (`2 * tau`) and is updated in the algorithm based on the error between the target and observed surprisal.
# LLAMA_API llama_token llama_sample_token_mirostat(struct llama_context * ctx, llama_token_data_array * candidates, float tau, float eta, int m, float * mu);
def llama_sample_token_mirostat(
    ctx: llama_context_p,
    candidates,  # type: _Pointer[llama_token_data_array]
    tau: c_float,
    eta: c_float,
    m: c_int,
    mu,  # type: _Pointer[c_float]
) -> int:
    return _lib.llama_sample_token_mirostat(ctx, candidates, tau, eta, m, mu)


_lib.llama_sample_token_mirostat.argtypes = [
    llama_context_p,
    llama_token_data_array_p,
    c_float,
    c_float,
    c_int,
    c_float_p,
]
_lib.llama_sample_token_mirostat.restype = llama_token


# @details Mirostat 2.0 algorithm described in the paper https://arxiv.org/abs/2007.14966. Uses tokens instead of words.
# @param candidates A vector of `llama_token_data` containing the candidate tokens, their probabilities (p), and log-odds (logit) for the current position in the generated text.
# @param tau  The target cross-entropy (or surprise) value you want to achieve for the generated text. A higher value corresponds to more surprising or less predictable text, while a lower value corresponds to less surprising or more predictable text.
# @param eta The learning rate used to update `mu` based on the error between the target and observed surprisal of the sampled word. A larger learning rate will cause `mu` to be updated more quickly, while a smaller learning rate will result in slower updates.
# @param mu Maximum cross-entropy. This value is initialized to be twice the target cross-entropy (`2 * tau`) and is updated in the algorithm based on the error between the target and observed surprisal.
# LLAMA_API llama_token llama_sample_token_mirostat_v2(struct llama_context * ctx, llama_token_data_array * candidates, float tau, float eta, float * mu);
def llama_sample_token_mirostat_v2(
    ctx: llama_context_p,
    candidates,  # type: _Pointer[llama_token_data_array]
    tau: c_float,
    eta: c_float,
    mu,  # type: _Pointer[c_float]
) -> int:
    return _lib.llama_sample_token_mirostat_v2(ctx, candidates, tau, eta, mu)


_lib.llama_sample_token_mirostat_v2.argtypes = [
    llama_context_p,
    llama_token_data_array_p,
    c_float,
    c_float,
    c_float_p,
]
_lib.llama_sample_token_mirostat_v2.restype = llama_token


# @details Selects the token with the highest probability.
# LLAMA_API llama_token llama_sample_token_greedy(struct llama_context * ctx, llama_token_data_array * candidates);
def llama_sample_token_greedy(
    ctx: llama_context_p,
    candidates,  # type: _Pointer[llama_token_data_array]
) -> int:
    return _lib.llama_sample_token_greedy(ctx, candidates)


_lib.llama_sample_token_greedy.argtypes = [
    llama_context_p,
    llama_token_data_array_p,
]
_lib.llama_sample_token_greedy.restype = llama_token


# @details Randomly selects a token from the candidates based on their probabilities.
# LLAMA_API llama_token llama_sample_token(struct llama_context * ctx, llama_token_data_array * candidates);
def llama_sample_token(
    ctx: llama_context_p,
    candidates,  # type: _Pointer[llama_token_data_array]
) -> int:
    return _lib.llama_sample_token(ctx, candidates)


_lib.llama_sample_token.argtypes = [
    llama_context_p,
    llama_token_data_array_p,
]
_lib.llama_sample_token.restype = llama_token


# /// @details Accepts the sampled token into the grammar
# LLAMA_API void llama_grammar_accept_token(struct llama_context * ctx, struct llama_grammar * grammar, llama_token token);
def llama_grammar_accept_token(
    ctx: llama_context_p,
    grammar: llama_grammar_p,
    token: llama_token,
) -> None:
    _lib.llama_grammar_accept_token(ctx, grammar, token)


_lib.llama_grammar_accept_token.argtypes = [
    llama_context_p,
    llama_grammar_p,
    llama_token,
]
_lib.llama_grammar_accept_token.restype = None

# Performance information


# LLAMA_API struct llama_timings llama_get_timings(struct llama_context * ctx);
def llama_get_timings(ctx: llama_context_p) -> llama_timings:
    return _lib.llama_get_timings(ctx)


_lib.llama_get_timings.argtypes = [llama_context_p]
_lib.llama_get_timings.restype = llama_timings


# LLAMA_API void llama_print_timings(struct llama_context * ctx);
def llama_print_timings(ctx: llama_context_p):
    _lib.llama_print_timings(ctx)


_lib.llama_print_timings.argtypes = [llama_context_p]
_lib.llama_print_timings.restype = None


# LLAMA_API void llama_reset_timings(struct llama_context * ctx);
def llama_reset_timings(ctx: llama_context_p):
    _lib.llama_reset_timings(ctx)


_lib.llama_reset_timings.argtypes = [llama_context_p]
_lib.llama_reset_timings.restype = None


# Print system information
# LLAMA_API const char * llama_print_system_info(void);
def llama_print_system_info() -> bytes:
    return _lib.llama_print_system_info()


_lib.llama_print_system_info.argtypes = []
_lib.llama_print_system_info.restype = c_char_p


# // Set callback for all future logging events.
# // If this is not called, or NULL is supplied, everything is output on stderr.
# LLAMA_API void llama_log_set(llama_log_callback log_callback, void * user_data);
def llama_log_set(
    log_callback: "ctypes._FuncPointer", user_data: c_void_p  # type: ignore
):
    return _lib.llama_log_set(log_callback, user_data)


_lib.llama_log_set.argtypes = [llama_log_callback, c_void_p]
_lib.llama_log_set.restype = None


# LLAMA_API void llama_dump_timing_info_yaml(FILE * stream, const struct llama_context * ctx);
def llama_dump_timing_info_yaml(stream: ctypes.c_void_p, ctx: llama_context_p):
    return _lib.llama_dump_timing_info_yaml(stream, ctx)

_lib.llama_dump_timing_info_yaml.argtypes = [ctypes.c_void_p, llama_context_p]
_lib.llama_dump_timing_info_yaml.restype = None


###################################################################################################


_llama_initialized = False

if not _llama_initialized:
    llama_backend_init(c_bool(False))
    _llama_initialized = True
