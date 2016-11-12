# Lafwebpy - Query the Hebrew OT

Lafwebpy is a python server (using `bottle`) that exposes ETCBC Hebrew data (using [`laf-fabric`](https://github.com/ETCBC/laf-fabric)) and provides api access to it to return (1) parsing data on words as well as (2) search results and (3) collocations based on search terms.

To interact with all this goodness, we need a fantastic frontend. Enter [`react-lafwebpy-client`](https://github.com/jcuenod/react-lafwebpy-client).* To use these repositories, clone them both to a parent directory. `Lafwebpy` is going to serve static content from `../react-lafwebpy-client/build` so directory structure is important. `React-lafwebpy-client` should be good to go (everything is built) but it uses webpack so you can `npm install` and start playing around with it if you so desire.

To run `Lafwebpy`, you need `laf-fabric` and `bottle`. You also need the [laf-fabric-data](https://github.com/ETCBC/laf-fabric-data) so follow the link and read the readme (it's short) and make sure you set up laf-fabric.cfg (in this folder, it's `.gitignore`d). Then cd into this directory and:

    python3 index.py

Finally, visit `localhost:8080/` in your favourite browser.

**NB: Make sure you have 4-6GB of RAM free before doing this or your machine may lock up...**

\* I find that naming projects kills them, so I prefer to giving them the clunkiest names that immediately spring to mind and that way I work night and day on making them awesome.
