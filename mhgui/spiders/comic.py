import scrapy
import lzstring
import subprocess
import json
import os

class ComicSpider(scrapy.Spider):
    name = "comic"
    allowed_domains = ["m.manhuagui.com"]
    start_urls = ["https://m.manhuagui.com/list/wanjie/view.html"]

    def parse(self, response):
        comic_list = response.xpath('//*[@id="detail"]/li')
        for comic in comic_list[1:2]:  ## 测试只用一个
            href = comic.xpath('./a/@href').extract_first()
            url = "https://m.manhuagui.com" + href ## eg:https://m.manhuagui.com/comic/19430/
            yield scrapy.Request(url, callback=self.parse_comic)

    def parse_comic(self, response):
        title = response.xpath('/html/body/div[1]/h1/text()').extract_first() ## eg:鬼灭之刃
        os.makedirs(f'./js/{title}', exist_ok=True)

        chapter_list = response.xpath('//*[@id="chapterList"]/ul/li')
        print(f'total_chapter: {len(chapter_list)}')

        for chapter in chapter_list: ## 测试只用一个
            href = chapter.xpath('./a/@href').extract_first() ## eg: /comic/19430/296021.html
            chapter_name = chapter.xpath('./a/b/text()').extract_first() ## eg: 鬼灭之刃 1000

            js_file = f'./js/{title}/{chapter_name}.js'
            if os.path.exists(js_file):
                print(f'{chapter_name}.js 已存在')
                continue

            url = "https://m.manhuagui.com" + href ## eg: https://m.manhuagui.com/comic/19430/585116.html
            yield scrapy.Request(
                            url, 
                            callback=self.parse_chapter,
                            cb_kwargs={
                                'title': title,
                                'chapter_name': chapter_name,
                            }
                        )

    def parse_chapter(self, response, title, chapter_name):
        js_code = response.xpath('/html/body/script[4]/text()').extract_first()
        js_code = str(js_code).replace(r'window["\x65\x76\x61\x6c"]', 'eval')

        split_string = js_code.split(',')[-3]
        compressed_string = split_string.split('\'')[1]

        x = lzstring.LZString()
        decompressed_string = x.decompressFromBase64(compressed_string)

        js_code = str(js_code).replace(split_string, '\'' + decompressed_string + '\'.split("|")')

        with open(f'./js/{title}/{chapter_name}.js', 'w', encoding='utf-8') as f:
            f.write(js_code)
        f.close()

        try:
            js_file = f'./js/{title}/{chapter_name}.js'
            result = subprocess.run(['node', js_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stdout
            error = result.stderr
        
            if result.returncode != 0:
                json_str = str(error).split('SMH.reader(')[1].split(').preInit();')[0]

                json_file = f'./json/{title}/{chapter_name}.json'
                os.makedirs(f'./json/{title}', exist_ok=True)
                with open(json_file, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(dict(json.loads(json_str)), indent=4, ensure_ascii=False))

                print(f'./json/{title}/{chapter_name}.json 已生成')
            else:
                pass
        finally:
            pass