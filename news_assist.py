import nltk
import re
import urllib.request
import bs4 as bs
import requests
import heapq
channel = "da2a92d2"

nltk.download('stopwords')

# search google assistant
tunnel = "https://" + channel + ".ngrok.io/searchG?text="

def search_google(query):
    print("before search")
    try:
        r = requests.get(tunnel + query)
        response = r.json()['response']
    except:
        response = [
            "I can't perform google search now! We'll fix it and be back."]
    print("after search")
    return response


def get_summary(link, num_sent):
    # adapted from https://stackabuse.com/text-summarization-with-nltk-in-python/
    # First, get article without references after sentences
    try:
        scraped_data = urllib.request.urlopen(link)
        article = scraped_data.read()
    except:
        article = "Sorry, I couldn't summarize this link."
        return article

    # print(article)
    parsed_article = bs.BeautifulSoup(article, 'lxml')

    paragraphs = parsed_article.find_all('p')

    article_text = ""

    for p in paragraphs:
        article_text += p.text

    # initial preprocessing
    article_text = re.sub('\:', ': ', article_text)
    article_text = re.sub('\.', '. ', article_text)
    n = 0
    while re.search('([.?!]+ +\d+) *', article_text):
        article_text = re.sub('([.?!]+ +\d+) *', '. ', article_text)
        n += 1

    # Second Removing special characters and digits
    formatted_article_text = re.sub('[^a-zA-Z.]', ' ', article_text)
    formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)

    # Get a sentence list
    sentence_list = nltk.sent_tokenize(article_text)

    # Get word frequencies
    stopwords = nltk.corpus.stopwords.words('english')

    word_frequencies = {}
    for word in nltk.word_tokenize(formatted_article_text):
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

    # Compute relative frequencies compared to the most frequent word
    try:
        maximum_frequncy = max(word_frequencies.values())
    except:
        maximum_frequncy = 1

    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)

    # Compute sentence score
    sentence_scores = {}
    for sent in sentence_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if "\r" not in sent and '\t' not in sent and '\n\n' not in sent:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]

    #print("here is the sentence_scores: ")
    # print(sentence_scores)

    # Use a max heap to compile a summary of the n sentences with maximum score
    if num_sent <= len(sentence_scores):
        summary_sentences = heapq.nlargest(
            num_sent, sentence_scores, key=sentence_scores.get)
    else:
        summary_sentences = heapq.nlargest(
            len(sentence_scores), sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)

    # Finally return
    if len(summary) > 100:
        return summary
    else:
        return "Sorry, I couldn't summarize this link."
