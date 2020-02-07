#coding:utf8
import os
import time
import datetime
import sys
import glob
from pprint import pprint
from google.cloud import storage
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums

# 変数設定
## GCSのバケット名を指定
bucketName = '<バケット名を記入してください>'
## https://cloud.google.com/speech-to-text/docs/languages?hl=ja
language = 'ja-JP'
## .wavの拡張子を記載
extention = '*.wav'
## ローカルPC上のクレデンシャルファイルを指定
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '<GCP上で生成したクレデンシャルファイルのPATHを記載してください>'

# 指定フォルダーからファイルリストを取得
def getFileList(path):
    print('start get file list: ', path)
    if os.path.isdir(path):
        # ディレクトリが存在
        target = os.path.join(path, '**', extention)
        list = glob.glob(target, recursive=True)
    else:
        # NG
        print('ERROR END')
        print('There is not input directory: ', path)
        print('#######')
        sys.exit(1)
    return list

# wavファイルかチェック
def checkWavFile(file):
    print('start check input file: ', file)
    if os.path.exists(file) and '.wav' == os.path.splitext(file)[-1].lower():
        # ファイルが存在して.wavファイルである
        print('#######')
        return True
    else:
        # NG
        print('There is not input file OR only .wav file: ', file)
        print('#######')
        return False

# wavファイルの情報を取得
def getWaveHeader(file, option=None):
    print('start check .wav file info: ', file)
    # -1は配列の一番後ろを指定するさいの設定方法/.lower()は小文字変換
    wavfile = open(file, 'rb')
    wav_header = {}
    wav_header['riff_chunk_id'] = wavfile.read(4).decode('ascii')
    wav_header['riff_chunk_size'] = int.from_bytes(wavfile.read(4), 'little')
    wav_header['riff_form_type'] = wavfile.read(4).decode('ascii')
    wav_header['fmt_chunk_id'] = wavfile.read(4).decode('ascii')
    wav_header['fmt_chunk_size'] = int.from_bytes(wavfile.read(4), 'little')
    wav_header['fmt_wave_format_type'] = int.from_bytes(wavfile.read(2), 'little')
    wav_header['fmt_channel'] = int.from_bytes(wavfile.read(2), 'little')
    wav_header['fmt_samples_per_sec'] = int.from_bytes(wavfile.read(4), 'little')
    wav_header['fmt_bytes_per_sec'] = int.from_bytes(wavfile.read(4), 'little')
    wav_header['fmt_block_size'] = int.from_bytes(wavfile.read(2), 'little')
    wav_header['fmt_bits_per_sample'] = int.from_bytes(wavfile.read(2), 'little')
    wav_header['data_chunk_id'] = wavfile.read(4).decode('ascii')
    wav_header['data_chunk_size'] = int.from_bytes(wavfile.read(4), 'little')
    wavfile.close()
    # degugのオプションが指定されたら上記の情報を出力
    if option == 'debug':
        pprint(wav_header)
        print('#######')
    print('#######')
    return wav_header['fmt_channel'], wav_header['fmt_samples_per_sec']

# ファイルアップロード
def uploadToGCS(file):
    print('start upload to gcs')
    client = storage.Client()
    bucket = client.get_bucket(bucketName)
    result = storage.Blob(bucket=bucket, name=os.path.basename(file)).exists(client)
    # GCS上にファイルが存在するかチェック
    if not result:
        # GCS上にファイルが存在しないためアップロードを実施
        try:
            blob = bucket.blob(os.path.basename(file))
            blob.upload_from_filename(file)
            print('done upload to gcs: ', file)
            print('#######')
        except Exception as e:
            print('uploadToGCS() is ERROR')
            print(e)
            print('#######')
    else:
        # GCS上にファイルが存在するためスキップ
        print('skip upload: ', file)
        print('#######')

# stt
def stt(file, channel, hertz, languageCode):
    print('exec stt: ', file)
    client = speech_v1.SpeechClient()
    config = {
            "language_code": languageCode,
            "sample_rate_hertz": hertz,
            "audio_channel_count": channel
        }
    targetDir, targetFile = os.path.split(file)
    gcsURL = f'gs://{bucketName}/{targetFile}'
    audio = {"uri": gcsURL}
    try:
        # アウトプット用ファイル設定
        outputFile = os.path.join(targetDir, 'STT_'+targetFile.replace('.wav', '.txt'))
        with open(outputFile, mode='w') as f:
            # STT実行
            operation = client.long_running_recognize(config, audio)
            response = operation.result()
            for result in response.results:
                # First alternative is the most probable result
                alternative = result.alternatives[0]
                print(u'Transcript: {}'.format(alternative.transcript))
                f.write('{}\n'.format(alternative.transcript))
            print('done stt: ', file)
            print('#######')
    except Exception as e:
        print('stt() is ERROR:')
        print(e)
        print('#######')

if __name__ == '__main__':
    # 開始時刻取得
    startTime = time.time()
    startDate = datetime.datetime.now()
    # 標準入力
    inputPath = input("ディレクトリのパスを入力してください: ")
    # 処理
    files = getFileList(inputPath)
    for file in files:
        print('## START: ', file)
        result = checkWavFile(file)
        if result:
            channel, hertz = getWaveHeader(file)
            uploadToGCS(file)
            stt(file, channel, hertz, language)
        else:
            continue
        print('## END: ', file)
    # 計測表示
    spendTime = time.time() - startTime
    endDate = datetime.datetime.now()
    print('start date: {0}'.format(startDate))
    print('end date: {0}'.format(endDate))
    print('spend time: {0}'.format(spendTime) + '[sec]')
