# 概要
- PythonでGoogle Speech to TextとGoogle Storageを使った音声テキスト化するツール

# 動作確認環境
- OS: Mac Catalina 10.15.2
- Python: 3.7.4

# pip

```
pip install google-cloud-speech
pip install google-cloud-storage
```

# 事前作業
- google storageにてバケットの作成
- google speech to text apiの有効化
- speech to text apiの認証ページにてサービスアカウントの作成を行う
- google storageのバケットのメニューから権限設定を確認し、上記で作成したサービスアカウントに対して読み込み・書き込み権限を付与する
- 最後にIAM/サービスアカウントページより上記作成のサービスアカウントページにてサービスアカウントキー(jsonファイル)をダウンロードする

# 実行方法
- ソースコードのバケット名とサービスアカウントキーのファイルパスを書き換えて以下を実行する

```
$ python gcp-stt.py 
ディレクトリのパスを入力してください: <音声ファイルが置かれたディレクトリパスを入力>
## START: sample/05.femal.normal.wav
start check input file: <ファイルパス>
#######
start check .wav file info: <ファイルパス>
#######
start upload to gcs
done upload to gcs: <ファイルパス>
#######
exec stt: <ファイルパス>
Transcript: ＜テキスト化結果＞
done stt: <ファイルパス>
#######
## END: <ファイルパス>
start date: YYYY-MM-DD HH:MM:SS.xxxxxx
end date: YYYY-MM-DD HH:MM:SS.xxxxxx
spend time: SS.xxxxxxxxxxxxx[sec]
```
