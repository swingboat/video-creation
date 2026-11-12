"""Sequential Gemma / connector lifetime for this 18GB host.

Uses the upstream encoder, weights and projection unchanged. Materializes
Gemma hidden states, releases the language model, then loads the connector.
The upstream default keeps both weight sets resident at once.
"""
import hashlib,os
import mlx.core as mx
from ltx_core_mlx.model.transformer.model import LTXModelConfig
from ltx_core_mlx.text_encoders.gemma.encoders.base_encoder import GemmaLanguageModel
from ltx_core_mlx.text_encoders.gemma.encoders.encoder_configurator import select_text_encoder
from ltx_core_mlx.text_encoders.gemma.feature_extractor import GemmaFeaturesExtractorV2
from ltx_core_mlx.utils.memory import aggressive_cleanup
from ltx_core_mlx.utils.weights import load_split_safetensors
from ltx_pipelines_mlx.utils.blocks import PromptEncoder

def install(root):
 cache=root/'.cache/prompt-embeddings';cache.mkdir(parents=True,exist_ok=True)
 def deferred_load(self):
  if select_text_encoder(self.model_dir)!='gemma3':raise ValueError('This project adapter is pinned to the Gemma 3 LTX-2.3 pack')
  self._encoder_kind='gemma3'
 def sequential_encode(self,prompt):
  key=hashlib.sha256(('LTX2.3-f306259-core0.18.0-sequential-v1:'+prompt).encode()).hexdigest()
  path=cache/(key+'.npz')
  if path.exists():
   values=mx.load(str(path));mx.eval(values['video'],values['audio']);print('Loaded cached prompt embeddings',flush=True);return values['video'],values['audio']
  deferred_load(self)
  print('Encoding prompt with Gemma only',flush=True)
  self._text_encoder=GemmaLanguageModel();self._text_encoder.load(self.gemma_model_id)
  states,mask=self._text_encoder.encode_all_layers(prompt,max_length=int(os.environ.get('LTX2_GEMMA_MAX_LENGTH','1024')))
  mx.eval(*states,mask)
  self._text_encoder=None;aggressive_cleanup()
  print('Projecting materialized hidden states with connector only',flush=True)
  precision=LTXModelConfig.from_checkpoint_dir(self.model_dir).double_precision_rope
  self._feature_extractor=GemmaFeaturesExtractorV2(double_precision_rope=precision)
  weights=load_split_safetensors(self.model_dir/'connector.safetensors',prefix='connector.')
  self._feature_extractor.connector.load_weights(list(weights.items()));del weights
  video,audio=self._feature_extractor(states,attention_mask=mask);mx.eval(video,audio)
  mx.savez(str(path),video=video,audio=audio)
  self._feature_extractor=None;del states,mask;aggressive_cleanup()
  print('Prompt ready; both text-model weight sets released',flush=True)
  return video,audio
 PromptEncoder.load=deferred_load
 PromptEncoder.encode=sequential_encode
