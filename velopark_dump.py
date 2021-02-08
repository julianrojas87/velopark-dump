import sys
import urllib.request
import urllib.parse
import ast
import rdflib
import csv

def get_as_list(url):
    return ast.literal_eval(urllib.request.urlopen(url).read().decode())

def query_graph(graph):
    return graph.query(
        """PREFIX schema: <http://schema.org/>
       PREFIX mv: <http://schema.mobivoc.org/>
       PREFIX gr: <http://purl.org/goodrelations/v1#>

       SELECT ?parking ?name ?owner ?address ?postCode ?email ?telephone ?section ?type ?capacity ?numberOfLevels ?covered ?website ?publicAccess ?temporarilyClosed ?intendedAudience ?osm ?latitude ?longitude ?shape ?freeOfCharge ?price
       WHERE {
        ?parking schema:name ?name ;
            mv:ownedBy [ gr:legalName ?owner ] ;
            schema:address [ schema:streetAddress ?address ] ; 
            schema:hasMap [ schema:url ?osm ] .
        OPTIONAL { ?parking schema:address [ schema:postalCode ?postCode ] }
        OPTIONAL {
            ?parking schema:contactPoint [
                    schema:email ?email ;
                    schema:telephone ?telephone
            ] .
        }
        OPTIONAL { ?parking vp:temporarilyClosed ?temporarilyClosed }
        OPTIONAL { ?parking schema:interactionService [ schema:url ?website ] }
        
        GRAPH ?g {
            ?section a ?type ;
                schema:geo [
                    a schema:GeoCoordinates ;
                    schema:latitude ?latitude ;
                    schema:longitude ?longitude
                ] .
                OPTIONAL {
                    ?section mv:totalCapacity ?capacity
                }
                OPTIONAL {
                    ?section schema:publicAccess ?publicAccess
                }
                OPTIONAL {
                    ?section mv:numberOfLevels ?numberOfLevels
                }
                OPTIONAL {
                    ?section vp:covered ?covered
                }
                OPTIONAL {
                    ?section vp:intendedAudience ?intendedAudience
                }
                OPTIONAL {
                    ?x schema:geo [
                        a schema:GeoShape ;
                        schema:polygon ?shape
                    ]
                }
                OPTIONAL {
                    ?section schema:priceSpecification [
                        mv:freeOfCharge ?freeOfCharge
                    ]
                }
                OPTIONAL {
                    ?section schema:priceSpecification [
                        schema:price ?price
                    ]
                }        
        }
        
       }""")

def get_total_capacity(data):
    capacity = 0
    sections = set()
    for row in data:
        if not list(row)[7] in sections:
            sections.add(list(row)[7])
            if(list(row)[9] is not None):
                capacity += int(list(row)[9])
    if capacity > 0:
        return capacity
    else:
        return ""

################ Main script logic #################
args = ast.literal_eval(str(sys.argv))
region = args[1]
data_list = []

# get list of parkings
parking_uris = get_as_list("https://velopark.ilabt.imec.be/rich-snippets-generator/api/" + region)
#parking_uris = ["https://velopark.ilabt.imec.be/data/NMBS_275"]

for p in parking_uris:
    print("--------------------------------------------")
    p_uri = urllib.parse.urlparse(p)
    print("getting data of parking: " , p_uri.geturl())
    # create a Graph
    g = rdflib.ConjunctiveGraph()
    # parse an RDF file hosted on the Web
    g.default_context.parse(p_uri.scheme + "://" + p_uri.netloc + "/" + urllib.parse.quote(p_uri.path))
    # extract data from graph with a SPARQL query
    data = list(query_graph(g))
    # calculate capacity considering parkings with multiple sections
    capacity = get_total_capacity(data)
    # organize data for CSV parsing
    relevant_row = list(data[0])
    relevant_row[9] = capacity
    relevant_row.pop(7)
    data_list.append(relevant_row)

with open("velopark_" + region + ".csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["parking", "name", "owner", "address", "postCode", "email",
                     "telephone", "type", "capacity", "numberOfLevels", "covered", "website", "publicAccess", 
                     "temporarilyClosed", "intendedAudience", "OpenStreetMap", "latitude", 
                     "longitude", "shape", "freeOfCharge", "price"])
    for row in data_list:
        writer.writerow(row)