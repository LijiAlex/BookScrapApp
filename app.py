import requests
from flask import Flask, render_template, request
from bs4 import BeautifulSoup as bs
from flask_cors import cross_origin
import csv

app = Flask(__name__)  # create a flask object

all_books = []


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homepage():
    try:
        global all_books
        if all_books == []:
            url = "https://thegreatestbooks.org/"
            uResponse = requests.get(url)
            page_html = bs(uResponse.text, "html.parser")  # finds html tags
            books = page_html.findAll("li", {"class": "item pb-3 pt-3 border-bottom"})  # get all books
            for b in books:
                book = {}
                try:
                    book["name"] = b.div.div.div.h4.findAll("a")[0].text
                except:
                    book["name"] = "No Name"
                try:
                    book["author"] = b.div.div.div.h4.findAll("a")[1].text
                except:
                    book["author"] = "No author"
                try:
                    bookLink = "https://thegreatestbooks.org" + b.div.div.div.h4.a["href"]
                    book["link"] = bookLink
                except:
                    book["link"] = "No link"
                try:
                    bookPage = requests.get(bookLink)
                    book_html = bs(bookPage.text, "html.parser")
                    page_elements = book_html.find_all('div', {'class': "row pt-3"})
                    book_details = page_elements[0]
                    try:
                        book["description"] = book_details.div.div.p.text
                    except:
                        book["description"] = "No description"
                    try:
                        book["buy"] = book_details.div.div.div.div.a["href"]
                    except:
                        book["buy"] = "No link"
                except:
                    book["description"] = "No description"
                    book["buy"] = "No link"
                all_books.append(book)
    except Exception as e:
        return 'something is wrong'
    return render_template("index.html")  # showcase an html page, by default it has to be in templates folder


@app.route('/search', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            search_book = request.form['book'].strip().lower()
            book_names = [book['name'].strip().lower() for book in all_books]
            if search_book in book_names:
                thebook = all_books[book_names.index(search_book)]
                return render_template('bookoutput.html', book=thebook)
            else:
                return render_template('results.html', books=all_books)
        except Exception as e:
            return 'something is wrong'

@app.route('/download', methods=['POST'])  # route to display the home page
@cross_origin()
def download():
    filename = "books.csv"
    f = open(filename, "w",encoding='utf-8')
    writer = csv.writer(f)
    header = ['Name', 'Author', 'Link', 'Description']
    writer.writerow(header)
    for book in all_books:
        writer.writerow([book['name'], book['author'], book['link'], book['description']])
    return "Written to csv"

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
    app.run(debug=True)
