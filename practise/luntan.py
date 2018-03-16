import requests
from bs4 import BeautifulSoup
import logging
import os
import queue
import threading

home = 'D:\\luntuan_girls3\\'


def save_img(url):
    try:
        global home
        rsp = requests.get(url)
        name = url.split('/')[-1]
        full_path = "%s%s" % (home, name)
        with open(full_path, 'wb') as fh:
            fh.write(rsp.content)
    except Exception as e:
        logging.error(e)


def get_all_img(src_link):
    logging.info(src_link)
    for s in src_link:
        save_img(s)


def all_girl_src_list(bs_obj):
    key = '小树医生心理生理医务室'
    p_list = bs_obj.find_all('p')
    girl_img_url_list = []
    for p in p_list:
        a = p.text
        if key in a:
            girl_tag = p.find_next_sibling('p')
            next_p = girl_tag.find_next('img')
            try:
                girl_src = next_p['src']
                girl_img_url_list.append(girl_src)
                break
            except Exception as e:
                logging.error("except: %s, obj:%s", e, next_p)

    logging.info(girl_img_url_list)
    return girl_img_url_list


def parse_one(url, header):
    logging.info(url)
    req_obj = requests.get(url, headers=header)
    bs_obj = BeautifulSoup(req_obj.text, 'html.parser')
    l = all_girl_src_list(bs_obj)
    get_all_img(l)


def parse_one_thread(q, header):
    my_name = threading.current_thread().name
    while 1:
        try:
            url = q.get()
            if url == 'END':
                logging.info('%s:END', my_name)
                break
            logging.info(url)
            req_obj = requests.get(url, headers=header)
            bs_obj = BeautifulSoup(req_obj.text, 'html.parser')
            l = all_girl_src_list(bs_obj)
            get_all_img(l)
        except Exception as e:
            logging.error("e:%s, url:%s", e, url)


def get_all_link(url, header):
    thread_num = 3
    req_obj = requests.get(url, headers=header)
    bs_obj = BeautifulSoup(req_obj.text, 'html.parser')
    all_a = bs_obj.find_all('a', {'class':'blog-title'})
    a_list = []
    for a in all_a:
        a_list.append(a['href'])
    logging.info(a_list)
    q_list = [queue.Queue() for i in range(thread_num)]
    t_list = [threading.Thread(target=parse_one_thread, args=(q, header)) for q in q_list]
    for t in t_list:
        t.start()
    index = 0
    for href in a_list:
        q_list[index].put(href)
        index += 1
        index = index % 10
        if index == 9:
            for t in t_list:
                if not t.is_alive():
                    logging.info("%s dead", t.name)
                    old_index = t_list.index(t)
                    old_queue = q_list[old_index]
                    new_t = threading.Thread(target=parse_one, args=(old_queue, header))
                    t_list.insert(old_index, new_t)
    for q in q_list:
        q.put("END")

if __name__ == "__main__":
    logging.basicConfig(filename='luntan.log', filemode='w', level=logging.DEBUG,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
    }
    try:
        if not os.path.exists(home):
            os.mkdir(home)
    except Exception as e:
        logging.error(e)
    for i in range(100):
        main_url = 'https://my.oschina.net/xxiaobian/blog/?sort=time&p=%d' % (i+1)
        get_all_link(main_url, header)