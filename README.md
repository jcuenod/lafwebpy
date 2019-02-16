# Not Maintained

Note, this project has been succeeded by [parabible](https://parabible.com). Code for the client available at https://github.com/parabible/parabible-server


## Lafwebpy - Query the Hebrew OT

Lafwebpy is a python server (using `bottle`) that exposes ETCBC Hebrew data (using [`text-fabric`](https://github.com/ETCBC/text-fabric/wiki)) and provides api access to it to return (1) parsing data on words as well as (2) search results and (3) collocations based on search terms.

To interact with all this goodness, we need a fantastic frontend. Enter [`react-lafwebpy-client`](https://github.com/jcuenod/react-lafwebpy-client).* To use these repositories, clone them both to a parent directory. `Lafwebpy` is going to serve static content from `../react-lafwebpy-client/build` so directory structure is important. `React-lafwebpy-client` should be good to go (everything is built) but it uses webpack so you can `npm install` and start playing around with it if you so desire.

To run `Lafwebpy`, you need `text-fabric` and `bottle`. You also need the [text-fabric-data](https://github.com/ETCBC/text-fabric-data). Then you just cd into this directory and:

    python3 index.py

Finally, visit `localhost:8080/` in your favourite browser.

Optionally, you can specify a port like this:

    python3 index.py 8000

**NB: Make sure you have 2-4GB of RAM free before doing this or your machine may lock up...**

\* I find that naming projects kills them, so I prefer to giving them the clunkiest names that immediately spring to mind and that way I work night and day on making them awesome. Lafwebpy is a legacy name that comes from laffabric - the previous implementation of what text-fabric now does a lot better.
