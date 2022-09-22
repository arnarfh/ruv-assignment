## RÚV assignment

The assignment was to return clips from the existing RÚv episode/clip endpoint
via a Proxy API. With the addition of return results based on the users(host)
location (ip-based).

The solution utilizes FastAPI for the REST endpoints, of which two are provided.

* /clips - Returns all clips in the current API, with the location as outside Iceland
* /clips/{search_string} - Returns all clips matching the search word

The process is as follows:

A user makes a request to the API for clips with a specific search string.

The application matches the users ip address to either company internal, inside Iceland, or foreign.

The application then fetches the newest data from the current API of RÚV, iterates
over the episodes and clips, taking the data that is needed for the new response,
as well as comparing the IP address (boolean) and changes the URL if needed.

This list is then returned to the user in a JSON format for utilizing on their part.

Example:

Query is made to the API: **/clips/covid**

Response:

    [{"data":[{"year-month":"2022-09","clips":[{"title":"Bið eftir endurhæfingu vegna covid","slug":"bid-eftir-endurhaefingu-vegna-covid","url":"https://ruv-vod.akamaized.net/opid/5207322T0/5207322T0.m3u8","time":"00:01:23","date":"2022-09-18"},{"title":"Covid-faraldrinum líklega næstum því lokið","slug":"covid-faraldrinum-liklega-naestum-thvi-lokid","url":"https://ruv-vod.akamaized.net/opid/5207322T0/5207322T0.m3u8","time":"00:03:34","date":"2022-09-18"}]},{"year-month":"2022-07","clips":[{"title":"Fjöldi Covid-Katta á Hrakhólum","slug":"fjoldi-covid-katta-a-hrakholum","url":"https://ruv-vod.akamaized.net/opid/5207244T0/5207244T0.m3u8","time":"00:17:43","date":"2022-07-12"}]}]}]