# 示例：使用pydub进行音频压缩
from pydub import AudioSegment

def optimize_audio(input_path, output_path, format='ogg', bitrate='128k'):
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format=format, bitrate=bitrate)