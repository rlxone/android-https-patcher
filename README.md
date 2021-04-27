<p align="center">
  <img width="300" height="300" src="https://user-images.githubusercontent.com/8312717/116280348-3cf94e00-a791-11eb-98b1-ab8fe33eb101.png" />
</p>

# Android HTTPS patcher
Patch your android app with self-signed certificate to sniff https traffic. Should work both release and debug builds.

## Usage
```
python apk_rebuild.py -i input.apk -o output.apk
```
Run python script and follow the instructions. After you've done drag output file into your emulator. Use `Charles`, `BurpSuite` or any other tooling for request sniffing.

## Requirements
- macOS
- [apktools](https://github.com/iBotPeaches/Apktool) (in your PATH)
- Android Studio (with Build Tools installed)
- Python 3

## Disclaimer
This repo was created for educational purposes only. Use it on your own risk.  
Have fun 😃
