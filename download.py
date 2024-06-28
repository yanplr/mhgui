import json
import os
import requests
import time
import threading
import glob

# https://i.hamreus.com/ps4/g/gmzr_wkhsq/第01回/JOJO_000.jpg.webp?e=1720432575&m=Fzx313l2F8iU9DT7dvWfDQ

def save_image(url, folder, name):
    headers = {
        'authority': 'i.hamreus.com',
        'accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://m.manhuagui.com/',
        'sec-ch-ua': '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'image',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42',
    }

    response = requests.get(url=url, headers=headers, stream=True)  
    # print(response.status_code)
    time.sleep(0.2)

    # 检查请求是否成功  
    if response.status_code == 200:  
        with open(os.path.join(folder, name), 'wb') as f:
            f.write(response.content)
        print(f"请求成功,{folder}/{name}")
    else:  
        print(f"请求失败，状态码：{response.status_code}")

def count_files_in_directory_by_pattern(directory, pattern, n):
    files = glob.glob(os.path.join(directory, pattern))
    return len(files) == n

if __name__ == '__main__':
    base_url = "https://i.hamreus.com"
    path = os.path.join(os.getcwd(), 'full_json')

    while True:
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if '.json' not in file:
                        continue
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    e = data['sl']['e']
                    m = data['sl']['m']
                    count = data['count']
                    
                    chapter = file.split('.')[0]
                    save_folder = os.path.join(root.replace('full_json', 'images'), chapter)
                    print(save_folder)
                    if not os.path.exists(save_folder):
                        os.makedirs(save_folder)
                    elif count_files_in_directory_by_pattern(save_folder, '*.jpg', int(count)):
                        print(f'{save_folder} 下载完成')
                        continue
                    else:
                        images = data['images']

                        threads = []
                        idx = 1
                        for image in images:
                            name = f"{str(idx).zfill(3)}.jpg"
                            if os.path.exists(os.path.join(save_folder, name)):
                                print(os.path.join(save_folder, name), '已存在')
                                idx += 1
                                continue
                            url = f"https://i.hamreus.com{image}?e={e}&m={m}"
                            threads.append(
                                threading.Thread(
                                    target=save_image,
                                    args=(url, save_folder,name)
                                )
                            )
                            idx += 1

                        for thread in threads:
                            thread.start()
                        for thread in threads:
                            thread.join()
        except Exception as e:
            print(e)