"""
MIT License

Copyright (c) 2020 Saphielle Akiyama

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
__title__ = 'Mio'
__author__ = 'Saphielle-Akiyama'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020 Saphielle-Akiyama'

from random import random, uniform
from discord import Embed, Color


class ColoredEmbed(Embed):
    """Haha yes"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = self.random_color
        
    @property
    def random_color(self):
        return Color.from_hsv(random(), uniform(0.75, 0.95), 1)
      
        
def chunker(to_chunk: list, chunk_size: int = 4):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(to_chunk), chunk_size):
        yield to_chunk[i:i + chunk_size]
