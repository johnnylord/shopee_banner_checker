# Shopee Banner Checker

## Prerequisites

### Install Project Dependencies
```bash
$ pip3 install -r requirements.txt
```

### Download Chrome Driver Downloader
Go to chrome driver [download](https://chromedriver.chromium.org/downloads) page, and install the driver to control chrome browser with python program. Unpack the downloaded driver into the `driver` directory (e.g `driver/chromedriver`)

## How to use the program
1. Prepare your target sellers urls in the input directory (e.g. `input/sellers.txt`)
```bash
# Inside the `input/sellers.txt`
https://shopee.tw/babyyy12345
https://shopee.tw/sunqunkang
https://shopee.tw/bobora
https://shopee.tw/iu.tw
```
2. Download banner images that must be included in the sellers' pages (e.g. `banner/banner.jpg`)
```bash
# 9/9 Campaign banner image
$ wget -O banner/banner.jpg https://cf.shopee.tw/file/af89f68f1538ceaf5a5231693b4ec191
```
3. Execute the scraper scripts
```bash
$ python3 main.py --input input/sellers.txt
```
4. Check the report file
```bash
$ cat report.txt
```
