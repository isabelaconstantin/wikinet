import pandas as pd
import numpy as np
import re
import wikipedia
import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import json
import urllib
from urllib.parse import urlencode
from urllib.request import urlopen
from collections import deque
# documentation: https://mwparserfromhell.readthedocs.io/en/latest/api/mwparserfromhell.nodes.html#module-mwparserfromhell.nodes.wikilink
import mwparserfromhell
import networkx as nx
import random
import argparse

from page_visits import getUserActivity

API_URL = "https://en.wikipedia.org/w/api.php"
# TODO: make it deal with server side error 
def parse_with_date(title, date=None):
    '''    
    :param title: title of the wikipedia article
    :param date: snapshot of the page as it was on the date. If None, scrapes the page as is now. 
    :return: the parsed page of wikipedia
    '''
    data = {"action": "query", "prop": "revisions", "rvlimit": 1,
            "rvprop": "content", "format": "json", "titles": title}
    if date is not None:
        data["rvstart"] = date
    raw = urlopen(API_URL, urlencode(data).encode()).read()
    res = json.loads(raw)
    try:
        text = list(res["query"]["pages"].values())[0]["revisions"][0]["*"]
    except KeyError as err:
        print("Key error {}".format(err))
        print(title)
        return None
    return mwparserfromhell.parse(text)


def preprocess_links(links):
    non_link = re.compile('Category:|File:|wikt:|.*#.*')
    links = [str(link.title) for link in links if non_link.match(str(link.title))==None]
    links = list(set(links))
    return links

def sample_links(n_links, n_links_sample, percentage_l, percentage_l_subsample):
    '''
    Example : make the first 20% of the links to account for 50% of the subsample
    :param n_links: number of links a page has
    :param n_links_sample: number of links you want to sample
    :param percentage_l: consider the top percentage_l links ..
    :param percentage_l_subsample: to account for percentage_l_subsample of the subsampled links
    :return:  the chosen links to select
    NOTE: if percentage_l = percentage_l_subsample => aprox uniform sampling 
    '''
    # no sampling needed here
    if n_links_sample >= n_links:
        return np.array(range(n_links))
    
    # how many links from the first group should be subsampled
    n_links_first_group = int(n_links_sample * percentage_l_subsample)
    # how many links from the first group we have
    n_links_first_group_pop = int(n_links * percentage_l)
    
    # no sampling from the first group
    if n_links_first_group_pop < n_links_first_group:
        links_chosen_group_1 = np.array(range(n_links_first_group_pop))
        remaining = n_links_sample - n_links_first_group_pop
        links_chosen_group_2 = np.random.choice(range(n_links_first_group_pop+1, n_links), size = remaining, replace= False)
        return np.append(links_chosen_group_1, links_chosen_group_2)
    
    # if we have to sample from both groups, create the probabilities 
    perc_1 = percentage_l_subsample / n_links_first_group_pop
    perc_2 = (1 - percentage_l_subsample) / (n_links - n_links_first_group_pop)
    #print('Links from first group were sampled with p ', perc_1, ' and links from second group were sampled with p ', perc_2)
    p = [perc_1] * n_links_first_group_pop + [perc_2] * (n_links - n_links_first_group_pop)
    chosen_links = np.random.choice(n_links, size = n_links_sample, p = p, replace=False)
    return chosen_links
    
def wiki_crawl(seed, date):
    # CONSTANTS: to be explored
    # max_nodes = 100
    # n_links_hop1 = 50 # how many direct neighbours
    max_nodes = 500
    n_links_hop1 = 175 # how many direct neighbours
    n_links_indirect_min = 10
    n_links_indirect_max = 25
    min_popularity = 30 # the minimum number of links a page should have to be taken into the graph (to avoid stubs or really small articles)

    # init algo
    article_links = {}
    queue = deque([seed])

    while(len(article_links) < max_nodes):
        if len(queue) == 0:
            print('no more links to dequeue')
            break
        article = queue.popleft()
        # crawl it
        article_content = parse_with_date(title=article, date=date)
        # check parse succesfull
        if article_content is not None:
            links = article_content.filter_wikilinks()
            links = preprocess_links(links)
            #print(len(links))
            if (len(links) > min_popularity):
                article_links[article] = links
                #print('Added ', article, ' to the graph')
                if article == seed:
                    idx_chosen_links = sample_links(n_links=len(links), n_links_sample=n_links_hop1, percentage_l=0.1, percentage_l_subsample=0.5)
                else:
                    '''
                    if len(links) > 100:
                        n_links_s = 50 # this is a hub, so get more links
                    else:
                        n_links_s = random.randint(n_links_indirect_min, n_links_indirect_max)
                    '''
                    n_links_s = random.randint(n_links_indirect_min, n_links_indirect_max)
                    idx_chosen_links = sample_links(n_links=len(links), n_links_sample=n_links_s, percentage_l=0.4, percentage_l_subsample=0.5 )
                for idx in idx_chosen_links:
                    if links[idx] not in article_links and links[idx] not in queue:
                        queue.append(links[idx])
    return article_links

def get_wikigraph_views(G, start, end):
    views = {}
    nodes_not_taken = []
    for node in G.nodes():
        try:
            views[node] = getUserActivity(article=node,
                                          granularity="daily",
                                          start=start,
                                          end=end,
                                          dateformat="iso")
        except KeyError:
            nodes_not_taken.append(node)
            print(f'KeyError for node "{node}"')

    views_graph = {}
    for node in G.nodes():
        if node not in views.keys():
            views_graph[node] = 1
            continue
        if len(views[node]) < 2 or views[node][0][0] == 0:
            views_graph[node] = 1
            continue

        try:
            # TODO: check dates are before & after the event            
            views_graph[node] = views[node][-1][0] / views[node][0][0]
        except IndexError:
            print(f'IndexError for node {node}')
            views_graph[node] = 1

    return views_graph


def construct_graph(links):
    G = nx.DiGraph()
    G.add_nodes_from(links.keys())
    for article in G.nodes():
        for link in links[article]:
            # add link if not self-loop
            if link in links and link != article:
                G.add_edge(article, link)
    return G

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', help='Continue from checkpoint graph', action='store_true')
    args = parser.parse_args()

    articles_w_date = [
        ('Stan Lee', '2018-11-12'),
        ('Stephen Hawking', '2018-03-14'),
        ('Alan Rickman', '2016-01-14')
    ]

    for article, datestr in articles_w_date:
        ndaysbefore = 1
        ndaysafter = 0
        date = datetime.datetime.strptime(datestr, '%Y-%m-%d')
        before = date - datetime.timedelta(days=ndaysbefore)
        after = date + datetime.timedelta(days=ndaysafter)

        outname = ''.join(c for c in article if c.isalnum())

        if not args.checkpoint:
            print(f'Crawl Wikipedia from {article}')
            links = wiki_crawl(article, after)
            G = construct_graph(links)

            print(f'nodes: {G.number_of_nodes()} edges: {G.number_of_edges()}')

            print(f'Writing {outname}_checkpoint.gpickle')
            nx.write_gpickle(G, outname+'.gpickle')

        print(f'Reading {outname}_checkpoint.gpickle')
        G = nx.read_gpickle(outname+'_checkpoint.gpickle')

        views_graph = get_wikigraph_views(G, before, after)

        print([(n, views_graph[n]) for n in list(views_graph.keys())[:10]])
        nx.set_node_attributes(G, values= views_graph, name = 'delta')

        outfile = outname+'.gpickle'
        print(f'{article} node views: {G.node[article]}')

        print(f'Writing {outfile}')
        nx.write_gpickle(G, outfile)
