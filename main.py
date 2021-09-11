import os
import os.path as osp
import re
import time
import shutil
import argparse
import subprocess
import multiprocessing

import cv2
import numpy as np
import pandas as pd
from requests_html import HTML
from selenium import webdriver


def check_banner(args):
    valid = False
    stage_dir = args[0]
    banner_dir = args[1]

    # Read banners to check
    banners = [ cv2.imread(osp.join(banner_dir, banner))
                for banner in os.listdir(banner_dir) ]
    count = len(banners)

    # Check downloaded images one by one
    for path in [ osp.join(stage_dir, f) for f in os.listdir(stage_dir) ]:
        # Read image
        img = cv2.imread(path)
        if img is None:
            continue
        # Match with banner
        for banner in banners:
            img = cv2.resize(img, (banner.shape[1], banner.shape[0]))
            ref = banner.astype('float')
            tar = img.astype('float')
            # Determine image volume
            volume = 1
            for v in img.shape:
                volume *= v
            # Perform difference between two image
            diff = np.sum(np.abs(ref-tar)) / volume
            if diff < 10:
                count -= 1
        # Early stopping
        if count <= 0:
            valid = True
            break

    return (osp.basename(stage_dir), valid)

def main(args):
    # Read target sellers to check their banner
    with open(args['input'], 'r') as f:
        sellers = [ line.strip('\n') for line in f.readlines() ]
        seller_names = [ osp.basename(seller) for seller in sellers ]

    # Instantiate chrome webdriver with default page google.com opened
    mobile_emulation = { "deviceName": "iPhone X" }
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    driver = webdriver.Chrome(args['driver'], options=chrome_options)
    driver.get('http://google.com')

    # Load every seller pages
    for name, seller in zip(seller_names, sellers):
        print(f"Open page '{name}'")
        driver.execute_script(f"window.open('about:blank', '{name}');")
        driver.switch_to.window(name)
        driver.get(seller)

    # Parse every opened pages
    pattern = r"https://cf.shopee.tw/file/[\d\w]+"
    for name in seller_names:
        # Create Staging directory for each seller
        stage_dir = osp.join(args['stage'], name)
        shutil.rmtree(stage_dir, ignore_errors=True)
        os.makedirs(stage_dir)
        # Extract links of each loaded images
        driver.switch_to.window(name)
        html = driver.page_source
        imgs = re.findall(pattern, html)
        # Download each loaded images
        print(f"Download images in '{driver.current_url}'")
        procs = []
        for img in imgs:
            cmdline = f'wget -O {osp.join(stage_dir, osp.basename(img))} {img}'
            proc = subprocess.Popen(
                                cmdline,
                                shell=True,
                                stderr=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL)
            procs.append(proc)
        # Wait for download completion
        for proc in procs:
            proc.wait()
            proc.terminate()

    # Exit the driver
    driver.quit()

    # Check banners with multiple workers
    stages = [ osp.join(args['stage'], seller) for seller in os.listdir(args['stage']) ]
    banners = [ args['banner'] ]*len(stages)
    tasks = list(zip(stages, banners))
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    results = pool.map(check_banner, tasks)

    data = { 'seller': [], 'result': [] }
    for result in results:
        data['seller'].append(result[0])
        data['result'].append(result[1])

    df = pd.DataFrame(data, columns=['seller', 'result'])
    df.to_csv(args['output'], index=False)
    print(f"Export result to {args['output']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="list of urls of target sellers")
    parser.add_argument("--output", default="report.txt", help="report file")
    parser.add_argument("--banner", default="banner", help="directory containing banners need to check")
    parser.add_argument("--stage", default="stage", help="staging directories to hold download images")
    parser.add_argument("--driver", default="driver/chromedriver")
    args = vars(parser.parse_args())
    main(args)
