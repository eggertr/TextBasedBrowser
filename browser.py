import os
import sys
import requests
from bs4 import BeautifulSoup
from colorama import init, Fore, Back, Style
init()

directory = ""
text_stack = []


class UserInput:

    def __init__(self, inp):
        self.inp_str = inp

    def is_url(self):
        if self.inp_str.rfind(".") > 0 and len(self.inp_str) - self.inp_str.rfind(".") == 4:
            return True

        return False

    def delete_dir(self):
        if os.path.exists(self.inp_str):
            os.rmdir(self.inp_str)


class WebPage:
    short_url = ""
    text = ""

    def __init__(self, _short):
        self.short_url = _short

        with open(os.path.join(directory, _short + ".txt"), "r", encoding="utf-8") as ifile:
            self.text = ifile.read()
        ifile.close()


class WebSite:
    short_url_list = []
    url = ""
    short_url = ""
    text = ""

    def __init__(self, url):
        self.url = url
        self.text = ""

        _idx = self.url.rfind(".")
        _end = self.url[_idx:]
        self.short_url = self.url.rstrip(_end)

        if self.short_url not in WebSite.short_url_list:
            WebSite.short_url_list.append(self.short_url)

        r = requests.get("HTTPS://" + url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'html.parser')
            self.text = soup.title.text

            if self.short_url == "docs.python":

                tags = soup.find_all(['h1', 'h3', 'p'])
                for tag in tags:
                    tag_link = list(tag.find_next('a'))

                    tag_line = tag.text.split('\n')
                    for i in range(0, len(tag_line)):
                        if tag_line[i] == tag_link[0]:
                            tag_line.insert(i, '{}'.format(Fore.BLUE))
                            tag_line.insert(i + 2, '{}'.format(Fore.RESET))
                            break

                    _line = " ".join(tag_line).replace("\x1b[34m ", "\x1b[34m").replace(" \x1b[39m", "\x1b[39m")
                    self.text += "\n" + _line.strip()

            else:
                # self.short_url == " annað url"
                # ----------------------------------------
                tags = soup.find_all(['h1', 'h2', 'h3', 'p', 'li', 'a', 'pre'])
                mylist = []
                trash_chars = ['|', '»']

                def rubbish(_text):
                    for _c in _text:
                        if _c in trash_chars:
                            return True
                    return False

                for tag in tags:

                    if not (tag.text == "" or rubbish(tag.text)):
                        if tag.has_attr('href'):
                            if rubbish(tag.attrs['href']):
                                continue

                        tag_c = tag.find_all()
                        for child_tag in tag_c:
                            if child_tag.has_attr('href'):
                                if rubbish(child_tag.attrs['href']):
                                    continue
                        mylist.append(tag)

                def add_link(_href, _text):
                    _color = "{}{}{}".format(Fore.BLUE, _href, Fore.RESET)
                    line = _text.replace(_href, _color, 1)
                    return line

                for item in mylist:
                    if item.name == 'h2':
                        _line = "\n"
                    if item.find('a'):
                        item_c = item.find('a')
                        if not rubbish(item_c.attrs['href']):
                            _line = add_link(item_c.text, " ".join(item.text.split("\n")))
                        mylist.remove(item)
                        continue
                    else:
                        if item.name == 'a':
                            _line = add_link(item.text, item.text)
                        else:
                            _line = item.text

                    self.text += "\n" + _line.strip()
                # ----------------------------------------
        else:
            print("Error reading URL: {}, code: {}".format(self.url, r.status_code))
            return

    def write_file(self):
        file_name = self.short_url + ".txt"
        with open(os.path.join(directory, file_name), "w", encoding="utf-8") as ofile:
            ofile.write(self.text)
            ofile.close()


def is_short_url(_url):
    if _url in WebSite.short_url_list:
        return True
    else:
        return False


def make_dir(_dir):
    global directory

    if not str.isprintable(_dir):
        print("Error making folder: {}".format(_dir))
    else:
        directory = _dir

        try:
            if not os.path.exists(_dir):
                os.mkdir(_dir)
            else:
                pass

        except OSError:
            print("Error making folder: {}".format(_dir))


def push_pop_stack(_arg, _txt):
    global tmp_text
    if _arg == "push":
        text_stack.append(_txt)
    elif _arg == "pop":
        if len(text_stack) > 0:
            print(text_stack.pop())

    tmp_text = ""


if len(sys.argv) > 0:
    make_dir(sys.argv[1])
else:
    print("No DIR argument!")

tmp_text = ""
lets_loop = True
while lets_loop:

    action = UserInput(input())

    if action.is_url():
        if tmp_text != "":
            push_pop_stack("push", tmp_text)

        web_site = WebSite(action.inp_str)
        web_site.write_file()
        print(web_site.text)
        tmp_text = web_site.text
        del web_site

    elif action.inp_str in WebSite.short_url_list:
        if tmp_text != "":
            push_pop_stack("push", tmp_text)

        web_page = WebPage(action.inp_str)
        print(web_page.text)
        tmp_text = web_page.text
        del web_page
    elif action.inp_str == "back":
        push_pop_stack("pop", "")
    elif action.inp_str == "exit":
        lets_loop = False
        continue
    else:
        print("error")

