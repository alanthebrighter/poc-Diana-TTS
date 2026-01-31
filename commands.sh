#!/bin/bash
rm -rf .diana-tts
python -m venv .diana-tts
# pip freeze > requirements
pip install -r requirements


# Adiciona tanto o cublas quanto o cudnn que você instalou via pip
#set -gx LD_LIBRARY_PATH /mnt/ssd-01-weijinto/code/poc-Diana-TTS/.diana-tts/lib/python3.13/site-packages/nvidia/cublas/lib/ /mnt/ssd-01-weijinto/code/poc-Diana-TTS/.diana-tts/lib/python3.13/site-packages/nvidia/cudnn/lib/ $LD_LIBRARY_PATH

# Verifique se o caminho foi adicionado corretamente
#echo $LD_LIBRARY_PATH
