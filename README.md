<p align="center">
  <img width="300" height="300" src="https://developer.android.com/guide/practices/ui_guidelines/images/NB_Icon_Mask_Shapes_Ext_02.gif" />
</p>

# Android HTTPS patcher
Patch your android app with self-signed certificate to sniff https traffic. Should work both release and debug builds.

## Usage
```
python apk_rebuild.py -i input.apk -o output.apk
```
Run python script and follow the instructions. After you've done drag output file into your emulator. Use `Charles`, `BurpSuite` or any other tooling for request sniffing.

### Before
![image](https://user-images.githubusercontent.com/8312717/116452741-b7e06880-a866-11eb-901a-d0a73cce8bb6.png)

### After
![image](https://user-images.githubusercontent.com/8312717/116452835-d5adcd80-a866-11eb-8046-75024f01004b.png)

## Requirements
- macOS or Windows
- [apktools](https://github.com/iBotPeaches/Apktool) (in your PATH)
- Android Studio (with Build Tools installed)
- Python 3.6 and above

## Disclaimer
This repo was created for educational purposes only. Use it on your own risk.  
Have fun 😃
