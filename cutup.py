from flask import Flask
from flask import render_template
from flask import request

import random
import boto
from boto.exception import SDBResponseError

#import re
from slugify import slugify

import config

#_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

app = Flask(__name__)

# create a global SimpleDB connection
# credentials in config file
sdb = boto.connect_sdb(config.aws['user'],config.aws['password'])

try:
    domain = sdb.get_domain('texts-production')
except SDBResponseError:
    domain = sdb.create_domain('texts-production')

@app.route('/acknowledgements')
def acknowledgements():
    """
    List of sources with links
    """
    acknowledgements = {
        "jQuery UI": "http://jqueryui.com",
        "Flask Python Web Framework": "http://flask.pocoo.org",
        "Sample 5-Paragraph Essay from Taft College OWL":
            "http://www.taftcollege.edu/instruct/LiberalArts/OWL/sampfive.htm",
    }
    return render_template('acknowledgements.html', acknowledgements=acknowledgements)


@app.route('/', methods=['POST', 'GET'])
@app.route('/submit', methods=['POST', 'GET'])
def submit():
    """
    Displays the form or the results of the cut-up text
    """
    if request.method == 'POST' and request.form['writing']:
        # split input on newlines, dumping empties produced by extra newlines
        # "filter" used to work on its own. Now I am forcing it in to a list
        # so that random.shuffle() will work on it correctly.
        stanzas = list(filter(None, request.form['writing'].splitlines()))
        # save original text
        original_entry = '\n'.join(stanzas)
        sdbtitle = slugify(request.form['title']) if request.form[
            'title'] else slugify(stanzas[0])
        doc = {'Title': request.form['title'], 'Author': request.form[
            'author'], 'Text': original_entry}
        try:
            domain.put_attributes(sdbtitle, doc)
        except SDBResponseError:
            # Stupid 1024 character limit
            pass
        random.shuffle(stanzas)
        return render_template('cutup.html',
                               title=request.form['title'],
                               author=request.form['author'],
                               stanzas=stanzas,
                               original=original_entry)
    else:
        # Nothing submitted. Back you go
        slugs = [{'slug': item.name, 'title': item['Title']}
                 for item in domain]
        return render_template('submit.html',
                               slugs=slugs)


@app.route('/delete-saves')
def delete_saves():
    domain.delete_item('junko')
    slugs = ''

    return render_template('submit.html',
                           slugs=slugs)


@app.route('/threeafricas')
def threeafricas():
    """
    Demo content
    A sample 5-paragraph essay
    """
    stanzas = [
        # intro
        "When many people hear the word Africa, they picture steaming jungles and gorillas. Hollywood films have shrunk"
        " the public image of this immense, varied continent into a small segment of its actual diversity. To have a "
        "more accurate picture of the whole continent, however, one should remember that there are, roughly, "
        "three Africas, each with its distinct climate and terrain and with a style of life suited to the environment."
        " The continent can be divided into the northern desert areas, the southeastern grasslands,"
        " and the tropical jungles to the southwest.",
        # body paragraph 1
        "The northern regions have the environment and living patterns of the desert. Egypt, Libya, Algeria, "
        "and Morocco have hot, dry climates with very little land suited to farming. Therefore, the population "
        "tends to be clustered into cities along rivers or the seacoast or into smaller settlements near oases."
        " For thousands of years, people have lived in this vast region, subsisting partly on what crops and animals "
        "they could raise and partly on trade with Europe.",
        # body paragraph 2
        "The southeastern grasslands provide a better environment for animal life and for some kinds of crops."
        " Many wild animals inhabit the plains in this region--elephants, giraffes, rhinoceros, antelopes, zebras,"
        " and lions. The people in this area have long been expert cattle raisers and hunters. Tea, coffee, cotton,"
        " cashew nuts, and tobacco are some of the main products grown in this region. Fishing also provides some food"
        " and income for people along the coast. The population here is less concentrated in cities and towns"
        " than in the north, but tends to be denser in areas where adequate rainfall and fertile soil"
        " make farming possible.",
        # body paragraph 3
        "West Africa is the region closest to the Hollywood image of mysterious jungles. As in the other two regions,"
        " the way people subsist depends upon their environment. This does not mean that most of the people live in"
        " grass huts in the jungle. Such nations as Nigeria have become highly modernized by income from oil, timber,"
        " and minerals. Most of the western countries have some farming that provides food and income; sugar cane,"
        " coffee, and tobacco are the important cash crops, while bananas, rice, and corn are raised for food."
        " Fishing in the rivers and along the coast also accounts for food and income, and precious stones,"
        " especially diamonds, enhance the economy of Angola and the Ivory Coast.",
        # conclusion
        "Even a superficial look at the major regions of Africa shows that it is a varied continent with "
        "several environments. Although most of the continent is tropical in its range of temperature, "
        "the climate ranges from deserts to rain forests. Similarly, human life-styles vary from the simplest"
        " rural villages to industrial cities, both new and ancient. Contrary to the myth, however, jungle life"
        " makes up only a very small portion of the whole of Africa."
    ]
    original = '\n'.join(stanzas)
    random.shuffle(stanzas)
    return render_template('cutup.html', title="The Three Africas", stanzas=stanzas, original=original)


@app.route('/icry')
def icry():
    """
    Sample poem: I Cry by Tupac Shakur
    """
    stanzas = [
        "Sometimes when I'm alone",
        "I Cry,",
        "Cause I am on my own.",
        "The tears I cry are bitter and warm.",
        "They flow with life but take no form",
        "I Cry because my heart is torn.",
        "I find it difficult to carry on.",
        "If I had an ear to confide in,",
        "I would cry among my treasured friend,",
        "but who do you know that stops that long,",
        "to help another carry on.",
        "The world moves fast and it would rather pass by.",
        "Then to stop and see what makes one cry,",
        "so painful and sad.",
        "And sometimes...",
        "I Cry",
        "and no one cares about why.",
    ]

    original = '\n'.join(stanzas)
    random.shuffle(stanzas)
    return render_template('cutup.html', title="I Cry", author="Tupac Shakur", stanzas=stanzas, original=original)


@app.route('/<slug>')
def display(slug):
    """
    Extract the text from the DB based on the RESTful URL
    """
    title = domain.get_item(slug)['Title']
    author = domain.get_item(slug)['Author']
    original = domain.get_item(slug)['Text']
    stanzas = list(filter(None, original.splitlines()))
    random.shuffle(stanzas)
    return render_template('cutup.html', title=title, author=author, stanzas=stanzas, orignal=original)


# Start it up! Don't leave debug on in production.
app.debug = config.debug
app.run(host='127.0.0.1')
