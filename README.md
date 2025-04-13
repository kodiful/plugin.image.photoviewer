## Kodiアドオン：フォトビューア

macOSの写真アプリケーションで管理されている写真をTV画面で閲覧するためのKodiアドオンです。
写真アプリケーションのデータベースを参照し、撮影日、撮影場所、顔画像認識による人物等にしたがって写真やビデオをブラウズできます。

macOS Sequoia（バージョン15.3.2）の写真アプリケーション（バージョン10.0 (741.0.130)）にて動作を確認しています。
Raspberry Pi OSにおいても、macOSの _写真ライブラリ.photoslibrary_ をあらかじめコピーしておき、このコピー先を写真ライブラリのパスとして設定することで動作することを確認しています。

はじめに[アドオン設定画面](#アドオン設定画面)で写真ライブラリへのパスを設定してください。

<br/>

## メイン画面

アドオン起動直後にメイン画面が表示されます。

![メイン画面](docs/images/01_日付.png)

<br/>

## 日付

写真の撮影日にしたがって年月日別にブラウズします。

![年選択](docs/images/10_日付/11_年選択.png)

![月選択](docs/images/10_日付/13_月選択.png)

![日選択](docs/images/10_日付/15_日選択.png)

### 日付のコンテクストメニュー

撮影日の絞り込み時に、年または月単位にまとめてブラウズできます。

![年選択のコンテクストメニュー](docs/images/10_日付/12_コンテクストメニュー.png)

![月選択のコンテクストメニュー](docs/images/10_日付/14_コンテクストメニュー.png)

<br/>

## ピープル

写真アプリが判定した顔画像にしたがって人物別にブラウズします。

![ピープル選択](docs/images/20_ピープル/21_選択.png)

<br/>

## モーメント

写真アプリが判定したモーメントにしたがってブラウズします。
各モーメントのおおよその位置から、緯度の高い順に（北から順に）表示します。

![モーメント選択](docs/images/30_モーメント/31_選択.png)

<br/>

## 写真一覧

日付、ピープル、モーメントでブラウズした結果が写真一覧として表示されます。
写真にGPS情報がある場合は _[GPS]_、ビデオの場合は _[VIDEO]_ が各項目の末尾に付記されます。

![写真一覧](docs/images/40_写真/41_一覧.png)

### 写真一覧のコンテクストメニュー

GPS情報がある写真（項目の末尾に _[GPS]_ が付記された写真）については、コンテクスメニューから選択して撮影地周辺の地図や撮影地周辺で撮影された写真を表示できます。

![写真一覧のコンテクストメニュー](docs/images/40_写真/42_コンテクストメニュー.png)

### 撮影地周辺の地図を表示

撮影地周辺の地図を表示します。
まずズーム選択で表示する地図の範囲を指定します。18段階のズームが設定できます。

![写真一覧のコンテクストメニュー](docs/images/40_写真/43_ズーム選択.png)

選択した範囲の地図が表示されます。中心の赤丸が選択した写真の撮影地の位置です。

![写真一覧のコンテクストメニュー](docs/images/40_写真/44_地図表示.png)

### 撮影地周辺の写真を検索

GPS情報があるすべての写真から、撮影地が[周辺撮影地検索範囲](#周辺撮影地検索範囲)内にある写真を検索して、[周辺撮影地検索上限](#周辺撮影地検索上限)まで近い順に表示します。

<br/>

## アドオン設定画面

![アドオン設定画面](docs/images/90_アドオン設定.png)

### 写真ライブラリへのパス

写真ライブラリへのパスを設定してください。
macOSのデフォルトでは _/Users/(username)/Pictures/写真ライブラリ.photoslibrary_ になります。

macOSでは _写真ライブラリ.photoslibrary_ のDBに直接アクセスするため、システム設定→プライバシーとセキュリティ→フルディスクアクセスで、Kodiにフルディスクアクセスを許可するよう事前に設定してください。
この許可が設定されていない場合、アドオン設定で _写真ライブラリ.photoslibrary_ が選択できません。

Raspberry Pi OSにおいても、macOSの _写真ライブラリ.photoslibrary_ をあらかじめコピーしておき、このコピー先を写真ライブラリのパスとして設定することで動作することを確認しています。

### 周辺撮影地検索範囲

[撮影地周辺の写真を検索](#撮影地周辺の写真を検索)する際の、検索範囲を指定します。

### 周辺撮影地検索上限

[撮影地周辺の写真を検索](#撮影地周辺の写真を検索)する際の、表示する検索結果の数の上限を指定します。



