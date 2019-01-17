import numpy as np
import datetime
import requests
import matplotlib.pyplot as plt

def getUserActivity(article, granularity, start, end, project ="en.wikipedia.org",
                    access="all-access", agent="user",dateformat="iso"):
    """
    Method to obtain user activity of a given page for a given period of time
    article: name of the wikiipedia article
    granularity: time granularity of activity, either 'monthly' or 'daily'
    start: start date of the research as Datetime.datetime object
    end: end date of the research as Datetime.datetime object
    project: If you want to filter by project, use the domain of any Wikimedia project (by default en.wikipedia.org)
    access: If you want to filter by access method, use one of desktop, mobile-app or mobile-web (by default all-access)
    agent: If you want to filter by agent type, use one of user, bot or spider (by default user).
    dateformat: the dateformat used in result array, can be 'iso','ordinal','datetime'.
    return:
        it return an array of array of the form [ [user_activity_value1, date1], [user_activity_value2, date2]]
    """

    #granularity['monthly','daily']
    #format['iso','ordinal','datetime']
    #Be carefull, for daily granularity left bound date is included, for monthly granularity left bound date is excluded
    
    dstart = start.strftime("%Y%m%d")
    dend = end.strftime("%Y%m%d")
    path = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"+project
            +"/"+access+"/"+agent+"/"+article+"/"+granularity+"/"+dstart+"/"+dend)
    r = requests.get(path)
    res = []
    for i in range(len(r.json()['items'])):
        time_label = None
        if granularity == 'daily':
            time_label = (start + datetime.timedelta(days=i))
        else:
            time_label = (start + relativedelta(months=+i))
        if dateformat == 'iso':
            time_label = time_label.isoformat()
        elif dateformat == 'ordinal':
            time_label = time_label.toordinal()
            
        res.append([r.json()['items'][i]['views'],time_label])
    return res


if __name__ == '__main__':
    articles_w_date = [
        ('Stan Lee', '2018-11-12'),
        ('Stephen Hawking', '2018-03-14'),
        ('Alan Rickman', '2016-01-14')
    ]

    ndaysbefore = 10
    ndaysafter = 20

    for article, datestr in articles_w_date:
        date = datetime.datetime.strptime(datestr, '%Y-%m-%d')
        start = date - datetime.timedelta(days=ndaysbefore)
        end = date + datetime.timedelta(days=ndaysafter)

        outname = ''.join(c for c in article if c.isalnum())

        views = getUserActivity(article=article,
                                granularity="daily",
                                start=start,
                                end=end,
                                dateformat="iso")

        y = [x[0] for x in views]
        x = np.arange(-ndaysbefore, ndaysafter+1)
        plt.plot(x, y)
        plt.title(article)
        plt.savefig(outname+'.png')
        plt.show()
