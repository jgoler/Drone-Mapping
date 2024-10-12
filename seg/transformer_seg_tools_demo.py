"""
Demo of segmentation tools with Hugging Face Transformers Library
"""


import torch
from PIL import Image
import requests
from transformers import SamModel, SamProcessor


