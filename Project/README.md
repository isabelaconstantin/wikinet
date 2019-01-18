# A Wikipedia Tour of Death: how University College Boat Club became popular

---

#### What is the goal of this project?
Using wikipedia data, this project aims to uncover how the death of a famous person impacts the number of views of neighboring wikipedia pages. We are doing three case studies, analysing the deaths of [Stephen Hawking](https://en.wikipedia.org/wiki/Stephen_Hawking), [Stan Lee](https://en.wikipedia.org/wiki/Stan_Lee), [Alan Rickman](https://en.wikipedia.org/wiki/Alan_Rickman).

`NetworkX`
#### What do you find in here ?
- _source_ contains all the code for this project. In it, you can find 3 notebooks and some helper functions in helpers:
* `1_DataAcquisition` notebook contains the pipeline for crawling wikipedia to obtain the subsampled graphs and the number of views for each wikipedia article at certain points in time.
* `2_DataExploration` notebook contains the pipeline for studying the network properties of the sampled graphs (i.e. diameter, clustering coefficient, degree distribution etc)
* `3_DataExploitation` notebook has the pipeline for analysing and visualising the number of page views for the nodes of the graph (i.e. our signal)

- You can read a detailed description of our project [here](https://github.com/isabelaconstantin/wikinet/blob/master/Project/Report/Report_NTDS.pdf)
- And in _data_ folder you can find the graphs we analysed (`*.gpickle`) and the corresponding signal on the nodes (`*_signal.pickle`)


---

#### Credits

[Isabela Constantin](https://github.com/isabelaconstantin) [Adélie Garin](https://github.com/hawewe), [Celia Hacker](https://github.com/celia07), [Michael Spieler](https://github.com/nuft)

