#!/usr/bin/env python3

__version__ = '1.0.0.post1'
import os
import sys
import requests as rs

from bs4 import BeautifulSoup as BS
from urllib.parse import unquote
from getpass import getpass


class AiubNotesDl:
    base_url = "https://portal.aiub.edu"
    course_url = base_url
    temp_url = base_url
    username = None
    password = None

    course_titles = []
    course_links = []

    course_pages = []

    sem_url = []

    count = 0
    sess = rs.session()

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def download_page(self):
        try:
            homepage = self.sess.post(
                self.base_url, data={
                    'username': self.username,
                    'password': self.password
                })
        except Exception:
            print("Unable to connect :( Check your netwrok connection.")
            sys.exit(0)
        homepage = homepage.content
        return homepage

    def parse(self):
        soup = BS(self.download_page(), 'html.parser')
        return soup

    def get_reg_url(self):
        soup = self.parse()
        try:
            soup = soup.findAll(
                'ul', attrs={'class': 'nav navbar-nav hidden-sm hidden-xs'})[0]
            soup = soup.findAll('a')[1]['href']
        except IndexError:
            print("Ooops ! Wrong ID/Pass or connectivity issue maybe.")
            sys.exit(0)
        self.course_url += str(soup)
        self.get_semesters(self.course_url)

    def get_semesters(self, url):
        data = self.sess.get(url).content
        newsoup = BS(data, "html.parser")
        newsoup = newsoup.find(
            'select', attrs={'class': 'btn btn-default form-control'})
        newsoup = newsoup.findAll('option')
        for each in newsoup:
            self.sem_url.append(self.temp_url + each['value'])

    def download_a_page(self, url):
        coursepage = self.sess.get(url).content
        soup = BS(coursepage, "html.parser")
        return soup

    def extract_course_page(self):
        self.sem_url.reverse()
        for each in self.sem_url:
            soup = self.download_a_page(unquote(each))
            soup = soup.find('tbody')
            soup = soup.findAll('a')
            for s in soup:
                t = s.string.replace('/', ',')
                t = t.split('-')[1]
                self.course_titles.append(t)
                self.course_links.append(self.base_url + s.get('href'))

    def get_course_pages(self):
        for link in self.course_links:
            resp = self.sess.get(link).content
            soup = BS(resp, "html.parser")
            self.course_pages.append(soup)

    def get_course_notes(self):
        i = 0
        n = self.username
        self.make_folder(n)
        os.chdir(n)
        for page in self.course_pages:
            soup = page.findAll('div', attrs={'class': 'col-md-12'})[1]
            soup = soup.findAll('a')

            # Making Folder for course notes
            folder_name = self.course_titles[i]
            self.make_folder(folder_name)
            os.chdir(folder_name)
            print("Downloading Notes Of "+self.course_titles[i].split('[')[0])
            if len(soup) != 0:
                for s in soup:
                    note_title = s.string
                    link = self.base_url+unquote(s.get('href'))
                    if note_title is not None and link is not None:
                        if not os.path.isfile(note_title):
                            self.dloader(note_title, link)
                print("Done")
            else:
                pass
            os.chdir('..')
            i += 1

        os.system('clear' if os.name == 'posix' else 'cls')
        print("Downloding Completed.....")
        print(str(self.count)+" new file/s added to the library")
        print("Check the directory where this programme is located..")

    def make_folder(self, name):
        current_dir = os.getcwd()
        final_directory = os.path.join(current_dir, name)
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

    def dloader(self, file_name, url):
        self.count += 1
        req = self.sess.get(url)
        file = open(file_name, 'wb')
        for chunk in req.iter_content(100000):
            file.write(chunk)
        file.close()

    def main(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Please wait for a while....")
        self.get_reg_url()
        self.extract_course_page()
        self.get_course_pages()
        self.get_course_notes()


def cli():
    username = input("Enter AIUB ID: ")
    password = getpass("AIUB Password: ")
    dl = AiubNotesDl(username, password)
    dl.main()
    dl.sess.close()


if __name__ == '__main__':
    cli()
