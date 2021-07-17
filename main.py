#!/usr/bin/python3

## Really really really quick and ugly script to fix nativefiers anoying limitations

from requests.exceptions import InvalidURL
from subprocess import Popen, PIPE
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from requests import get
from os import makedirs
from re import search
from sys import argv

global DESKTOP_PATH, ICON_PATH
DESKTOP_PATH = "/usr/share/applications/"
ICON_PATH = "/usr/share/icons/nativefier/"


def get_title(url):
    r = get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    try:
        return soup.title.text
    except AttributeError:
        return ""


def download_favicon(url, path=ICON_PATH):
    def get_favicon_url(domain):
        page = get(domain)
        soup = BeautifulSoup(page.text, features="lxml")
        icon_link = soup.find("link", rel="shortcut icon")
        if icon_link is None:
            icon_link = soup.find("link", rel="icon")
        if icon_link is None:
            return domain + '/favicon.ico'
        icon_url = icon_link["href"]
        print(icon_url)
        full_url =  url.split("//")[0] + icon_url if not "http" in icon_url else icon_url

    favicon_url = get_favicon_url(url)
    icon = get(favicon_url)


    file_name = name + "-nativefier-icon.ico"

    try:
        makedirs(path, exist_ok=0)
    except FileExistsError:
        pass

    with open(path + file_name, "wb") as f:
        f.write(icon.content)
    return path + file_name


def create_desktop_icon(executable_path, file_path=DESKTOP_PATH):
    global title, name, favicon_path

    def build_desktop_icon_str(executable_path, icon_path=favicon_path, comment=title, name=name):
        return f"""[Desktop Entry]
Version=1.0
Name={name}
Comment={comment}
Exec={executable_path}
Icon={icon_path}
Terminal=false
Type=Application
    """

    icon_str = build_desktop_icon_str(executable_path)
    file_name = file_path + name + "-nativefier.desktop"
    with open(file_name, "w") as desktop_icon:
        desktop_icon.write(icon_str)


def run_command(url):
    command = f"nativefier {' '.join(argv[2:])} --name={name} {url}"
    p = Popen(command, stdout=PIPE, shell=1)
    command_output = p.stdout.read().decode("utf-8")
    command_path = search("(?<=App built to )(.*)(?=, move to wherever it makes sense)", command_output).group(1)
    return command_path


def run(url):
    global name, title, favicon_path, executable_path, title
    name = urlparse(url).netloc.split(".")[-2:-1][0].capitalize()
    title = get_title(url)
    favicon_path = download_favicon(url)
    executable_path = run_command(url)
    executable_path += "/"
    executable_path += "-".join(executable_path.split("/")[-2].split("-")[:-2])
    create_desktop_icon(executable_path)


if __name__ == "__main__":
    try:
        url = argv[1]
    except IndexError:
        exit("[!] Please enter an url")
    run(url)
