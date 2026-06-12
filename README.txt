わたしの蔵書館 — Streamlit版
==============================

■ ファイル構成
  app.py                  … アプリ本体
  requirements.txt        … 必要な部品(Streamlit Cloudが自動で読みます)
  .streamlit/config.toml  … 配色テーマ

■ Streamlit Cloud での公開手順
  1. GitHubのリポジトリ(例:hondana)の中身を、この3つに置き換える
     ※ requirements.txt を忘れずに(これが無いとエラーになります)
     ※ .streamlit フォルダごとアップロードしてください
  2. Streamlit Cloud側は自動で再読み込みされます
     (されない場合は Manage app → Reboot)

■ 大事な注意
  - Streamlit Cloud のサーバーは再起動するとデータが消えることがあります。
    サイドバー下の「バックアップ」からときどきダウンロードしてください。
    消えたときは同じ場所から復元できます。
  - URLを知っている人は誰でも同じ本棚を見て・編集できます。
    自分専用にしたい場合は、Streamlit Cloud の設定でアプリを
    非公開(Private)にできます。

■ 手元のパソコンで試す場合
  pip install streamlit
  streamlit run app.py
